#PSP_visual3D.py
from __future__ import division

from PSP_dataStructures import *
from PSP_color import *
from PSP_fileUtilities import loadState, saveState
import PSP_balance as balance
import PSP_tin as tin
import PSP_soil as soil
from copy import copy
import visual
import sys

surfaceTriangles = []
subSurfaceTriangles = []
colorScale = []
visualizedLayer = 1
nrColorLevels = 10
degreeMaximum = 1
degreeMinimum = 0.5
isPause = False
currentPrec = 0.0
  
def updateLayer(s):
    global visualizedLayer, degreeMinimum, degreeMaximum
    if s == 'd':
        visualizedLayer = min(visualizedLayer+1, C3DStructure.nrLayers-1)
    elif s == 'u':
        visualizedLayer = max(visualizedLayer-1, 1)
    elif s == 'c':
        rangeOk = False
        while not rangeOk:
            degreeMinimum = input("\nSet min. value (Degree of saturation):")
            degreeMaximum = input("Set max. value (Degree of saturation):")
            if degreeMaximum <= degreeMinimum:
                print("Wrong range!")
            else:
                rangeOk = True
    updateInterface()
    drawSubSurface(False)
                
def keyInput(evt):
    global isPause
    s = evt.key
    if s == 'd' or s == 'u' or s== 'c':
        updateLayer(s)
    elif s == 'p':
        isPause = True
        print ("Pause! \nPress 'r' to restart")
    elif s == 'r':
        isPause = False
    elif s == 's':
        isPause = True
        print ("Save State... \nPress 'r' to restart")
        saveState()
    elif s == 'l':
        isPause = True
        print ("Load State... \nPress 'r' to restart")
        if loadState():
            balance.initializeBalance()
            redraw(False)
    while isPause:
        visual.wait()
            
        
def getDisplay(x0, y0, dx, dy, brightness, title):
    cX = (tin.header.xMin + tin.header.xMax) * 0.5
    cY = (tin.header.yMin + tin.header.yMax) * 0.5
    cZ = tin.header.zMin #(header.zMin + header.zMax) * 0.5
    display = visual.display(x = x0, y = y0, width = dx, height = dy, exit=True)
    display.title = title
    display.background = visual.color.white
    display.ambient = brightness
    display.center = (cX, cY, cZ*tin.header.magnify)
    display.up = (0,0,1)
    display.forward = (0.33, -0.33, -0.15)
    return display

def InitializeInterface(x0, y0, dx, dy):
    global interface, layerLabel, timeLabel, precLabel, stepLabel, storageLabel
    global flowLabel, totalFlowLabel, totalErrorLabel, colorScale
    interface = visual.display(x = x0, y = y0, width = dx, height = dy, exit=True)
    interface.title = "Criteria3D"
    interface.background = visual.color.white
    interface.foreground = visual.color.black
    interface.range = 6.5
    interface.center = (-1, 0.5, 0)
    h = int(dy / 35)
    layerLabel = visual.label(height=h, y = 5.5, text = "", display = interface)
    visual.label(height=h, y = 4.5, text = "Press 'u':up  'd':down ", display = interface)
    visual.label(height=h, y = 3.5, text = "'p':pause 'c':colorscale", display = interface)
    visual.label(height=h, y = 2.5, text = "'s':save state", display = interface)
    timeLabel = visual.label(height=h, y = 1, text = "", display = interface)
    stepLabel = visual.label(height=h, y = 0, text = "", display = interface)
    precLabel = visual.label(height=h, y = -1, text = "", display = interface)
    storageLabel = visual.label(height=h, y = -2, text = "", display = interface)
    flowLabel = visual.label(height=h, y = -3, text = "", display = interface)
    totalFlowLabel = visual.label(height=h, y = -4, text = "", display = interface)
    totalErrorLabel = visual.label(height=h, y = -5, text = "", display = interface)
    stepY = 10 / nrColorLevels
    h = int(interface.height / (nrColorLevels * 3.5))
    for i in range (nrColorLevels+1):
        l = visual.label(x=-4, y=-5+(i*stepY), height=h, display = interface)
        colorScale.append(l)
    
def initialize(totalWidth):
    global surface, subSurface
    setColorScaleTIN()
    setColorScaleSurfaceWater()
    setColorScaleDegreeOfSaturation()
    interfaceWidth = totalWidth * 0.2
    dx = int((totalWidth-interfaceWidth) / 2.0)
    dy = dx * 0.8
    surface = getDisplay(0, 0, dx, dy, 1.0, "Surface")
    subSurface = getDisplay(dx, 0, dx, dy, 1.0, "Soil")
    InitializeInterface(dx*2, 0, interfaceWidth, dy)
    surface.bind('keydown', keyInput) 
    subSurface.bind('keydown', keyInput)
    interface.bind('keydown', keyInput)
       
def cleanAll(elements):
    for i in range(len(elements)):
        elements[i].visible = False
    del elements[:]       
    
def getNewTriangle(myColor, myDisplay, v):
    newTriangle = visual.faces(color=myColor, pos = v, display = myDisplay)
    newTriangle.make_twosided()
    return newTriangle
    
def drawSurface(isFirst):
    maximum = 0.05
    for i in range(C3DStructure.nrTriangles):
        v = copy(tin.C3DTIN[i].v)
        v[:,2] *= tin.header.magnify
        z = tin.C3DTIN[i].centroid[2]
        TINColor = getTINColor(z, tin.header)
        waterHeight = max(C3DCells[i].H - C3DCells[i].z, 0.0)
        waterColor = getSurfaceWaterColor(waterHeight, maximum)
        
        if waterHeight > maximum: a = 1
        elif waterHeight < EPSILON_METER: a = 0.0
        else: a = max(0.2, waterHeight / maximum)
        myColor = a*waterColor + (1-a)*TINColor
        
        if (isFirst):
            newTriangle = getNewTriangle(myColor, surface, v)
            surfaceTriangles.append(newTriangle)
        else:
            surfaceTriangles[i].color = myColor  
    if sys.version_info < (3, 0): visual.wait()
 
 
def drawSubSurface(isFirst):
    for i in range(C3DStructure.nrTriangles):
        v = copy(tin.C3DTIN[i].v)
        v[:,2] *= tin.header.magnify
        index = visualizedLayer * C3DStructure.nrTriangles + i
        myColor = getSEColor(C3DCells[index].Se, degreeMinimum, degreeMaximum)
        if (isFirst):
            newTriangle = getNewTriangle(myColor, subSurface, v)
            subSurfaceTriangles.append(newTriangle)
        else:
            subSurfaceTriangles[i].color = myColor   
    if sys.version_info < (3, 0): visual.wait()  
    
def updateInterface():
    if C3DParameters.computeOnlySurface:
        layerLabel.text = "Visualized layer: 0"
    else:
        depth = soil.depth[visualizedLayer] * 100
        layerLabel.text = "Degree of saturation " + format(depth,".1f")+"cm"
        
    timeLabel.text = "Time: " + str(int(balance.totalTime)) + " [s]"
    precLabel.text = "Prec: " + str(currentPrec) + " [mm/hour]"
    storage = balance.currentStep.waterStorage
    flow = balance.currentStep.waterFlow
    timeStep = C3DParameters.currentDeltaT
    totalFlow = balance.allSimulation.waterFlow
    totalError = balance.allSimulation.MBE
    stepLabel.text = "Time step: " + str(timeStep) +" [s]"
    storageLabel.text = "Storage: " + format(storage,".2f") +" [m3]"
    flowLabel.text = "Flow: " + format(flow,".4f") + " [m3]"
    totalFlowLabel.text = "Total flow: " + format(totalFlow,".3f") + " [m3]"
    totalErrorLabel.text = "Total error: " + format(totalError,".3f") + " [m3]"
    step = (degreeMaximum - degreeMinimum) / nrColorLevels
    for i in range (nrColorLevels+1):
        degree = degreeMinimum + step * i
        colorScale[i].background = getSEColor(degree, degreeMinimum, degreeMaximum)
        colorScale[i].text = format(degree,".2f")
    if sys.version_info < (3, 0): 
        visual.wait()
    
def redraw(isFirst):
    updateInterface()
    drawSurface(isFirst)
    if not C3DParameters.computeOnlySurface:
        drawSubSurface(isFirst)
      
    
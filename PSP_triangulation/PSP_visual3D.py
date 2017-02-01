#PSP_visual3D.py
from __future__ import division
import visual
import sys
from copy import copy
from PSP_color import *

NODATA = -9999

pointList3D = []
pointListDtm3D = []
triangleList3D = []
surfaceList3D = []

global TINScene, DTMScene

def initialize(header):
    global TINScene, DTMScene
    cX = header.xllCorner + header.nrCols * header.cellSize * 0.5
    cY = header.yllCorner + header.nrRows * header.cellSize * 0.45
    cZ = header.zMin + header.dz * 0.5
    DTMScene = visual.display(x = 0, y = 0, width = 600, height = 600)
    DTMScene.title = "DTM"
    DTMScene.background = visual.color.white
    DTMScene.ambient = 0.33
    DTMScene.center = (cX, cY, cZ*header.magnify)
    DTMScene.forward = (0, 1, -1)
    
    TINScene = visual.display(x = 600, y = 0, width = 600, height = 600)
    TINScene.title = "TIN"
    TINScene.background = visual.color.white
    TINScene.ambient = 0.33
    TINScene.center = (cX, cY, cZ*header.magnify)
    TINScene.up = (0,0,1)
    TINScene.forward = (0, 1, -1)
    setColorScaleDtm()

def drawDTM(pointList, header):
    for i in range(len(pointList)):
        p = pointList[i]
        myColor = getDTMColor(p[2], header)
        myPos = ([p[0], p[1], p[2] * header.magnify])
        myPoint = visual.points(display = DTMScene, pos = myPos, 
                                    size = 3.0, color=myColor) 
        pointListDtm3D.append(myPoint)
    key = DTMScene.kb.getkey()

def cleanAllPoints():
    while (len(pointList3D) > 0):
        pointList3D[0].visible = False
        myPoint = pointList3D.pop(0)
        del myPoint
 
def delTriangle(i):
    triangleList3D[i].visible = False 
    myTriangle = triangleList3D.pop(i)
    del myTriangle
           
def cleanAllTriangles():
    lastIndex = len(triangleList3D) - 1
    for i in np.arange(lastIndex, -1, -1):
        delTriangle(i)
    
def cleanAll():
    cleanAllPoints()
    cleanAllTriangles()
    
def drawSurface(myColor, v):
    mySurface = visual.faces(display = TINScene, color=myColor, pos = v)
    mySurface.make_twosided()
    mySurface.make_normals()
    mySurface.smooth()
    surfaceList3D.append(mySurface)

def drawAllPoints(pointList, header):
    cleanAll()
    myPosition = []
    for i in range(len(pointList)):
        p = pointList[i]
        myPosition.append([p[0], p[1], p[2] * header.magnify])
    myPoints = visual.points(display = TINScene, pos = myPosition, size = 3.0, 
                             color=visual.color.black) 
    pointList3D.append(myPoints)
    #key = TINScene.kb.getkey()
 
def addTriangle(index, triangle, header):
    v = copy(triangle.v)
    v[:,2] *= header.magnify
    myTriangle = visual.curve(pos=[v[0],v[1],v[2],v[0]], 
                                  color=visual.color.black)
    triangleList3D.insert(index, myTriangle)  
    if sys.version_info < (3, 0): visual.wait()
         
def drawAllTriangles(triangleList, header):
    cleanAll()
    for i in range(len(triangleList)):
        addTriangle(i, triangleList[i], header)
    #key = TINScene.kb.getkey()
        
def drawAllSurfaces(triangleList, header):
    cleanAll()
    nrTriangles = len(triangleList)
    for i in range(nrTriangles):
        v = copy(triangleList[i].v)
        z = sum(v[:,2]) / 3.0
        myColor = getDTMColor(z, header)
        v[:,2] *= header.magnify
        drawSurface(myColor, v)
    if sys.version_info < (3, 0): visual.wait()
    

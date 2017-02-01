from __future__ import print_function, division
from PSP_criteria3D import *
from PSP_readDataFile import readDataFile
import PSP_visual3D as visual3D
import PSP_tin as tin
import numpy as np
 
def main():     
    print ("Load TIN...")
    vertexList, isFileOk = readDataFile("data/vertices.csv", 0, ",", False)
    if (not isFileOk): return 
    triangleList, isFileOk = readDataFile("data/triangles.csv", 0, ",", False) 
    if (not isFileOk): return 
    nrTriangles = len(triangleList)
    neighbourList, isFileOk = readDataFile("data/neighbours.csv", 0, ",", False) 
    if (not isFileOk): return 
    print ("Nr. of triangles:", nrTriangles)
    
    v = np.zeros((3, 3), float)
    for i in range(nrTriangles):
        for j in range(3):
            v[j] = vertexList[int(triangleList[i,j])]
        tin.C3DTIN.append(tin.Ctriangle(v))
        C3DStructure.totalArea += tin.C3DTIN[i].area
    print ("Total area [m^2]:", C3DStructure.totalArea)
    
    tin.header = tin.getHeader(tin.C3DTIN)
    
    print ("Set boundary...")
    for i in range(nrTriangles):
        tin.C3DTIN[i].isBoundary = False
        if (neighbourList[i,2] == NOLINK):
            tin.C3DTIN[i].isBoundary = True
            tin.getBoundaryProperties(tin.C3DTIN, i, neighbourList[i])
    
    print ("Load soil...")
    soil.C3DSoil = soil.readHorizon("data/soil.txt", 1)
    if (C3DParameters.computeOnlySurface):
        totalDepth = 0
    else:
        totalDepth = soil.C3DSoil.lowerDepth
    print("Soil depth [m]:", totalDepth)
    
    nrLayers, soil.depth, soil.thickness = soil.setLayers(totalDepth, 
                     C3DParameters.minThickness, C3DParameters.maxThickness, 
                     C3DParameters.geometricFactor) 
    print("Nr. of layers:", nrLayers) 
    print("Depth:", soil.depth)
    
    # Initialize memory
    memoryAllocation(nrLayers, nrTriangles)
    print("Nr. of cells: ", C3DStructure.nrCells)
    
    print("Set cell properties...")   
    for i in range(nrTriangles):
        for layer in range(nrLayers): 
            [x, y, z] = tin.C3DTIN[i].centroid 
            index = i + nrTriangles * layer
            elevation = z - soil.depth[layer]
            volume = float(tin.C3DTIN[i].area * soil.thickness[layer])
            setCellGeometry(index, x, y, 
                                elevation, volume, tin.C3DTIN[i].area)
            if (layer == 0):
                # surface 
                if tin.C3DTIN[i].isBoundary:
                    setCellProperties(index, True, BOUNDARY_RUNOFF)
                    setBoundaryProperties(index, 
                                  tin.C3DTIN[i].boundarySide, tin.C3DTIN[i].boundarySlope)
                else:
                    setCellProperties(index, True, BOUNDARY_NONE)
                setMatricPotential(index, 0.0)
                
            elif (layer == (nrLayers-1)):
                # last layer
                if C3DParameters.isFreeDrainage:
                    setCellProperties(index, False, BOUNDARY_FREEDRAINAGE)
                else:
                    setCellProperties(index, False, BOUNDARY_NONE)
                setMatricPotential(index, C3DParameters.initialWaterPotential)
                
            else:
                if tin.C3DTIN[i].isBoundary: 
                    setCellProperties(index, False, 
                                BOUNDARY_FREELATERALDRAINAGE)
                    setBoundaryProperties(index, tin.C3DTIN[i].boundarySide 
                                    * soil.thickness[layer], tin.C3DTIN[i].boundarySlope)
                else:
                    setCellProperties(index, False, BOUNDARY_NONE)
                setMatricPotential(index, C3DParameters.initialWaterPotential)
                 
    print("Set links...")   
    for i in range(nrTriangles): 
        # UP
        for layer in range(1, nrLayers):
            exchangeArea = tin.C3DTIN[i].area
            index = nrTriangles * layer + i 
            linkIndex = index - nrTriangles
            SetCellLink(index, linkIndex, UP, exchangeArea)   
        # LATERAL
        for j in range(len(neighbourList[i])):
            neighbour = int(neighbourList[i,j])
            if (neighbour != NOLINK):
                linkSide = tin.getAdjacentSide(i, neighbour,
                                        vertexList, triangleList)
                for layer in range(nrLayers): 
                    if (layer == 0):
                        #surface: boundary length [m]
                        exchangeArea = linkSide
                    else:
                        #sub-surface: boundary area [m2]
                        exchangeArea = soil.thickness[layer] * linkSide
                    index = nrTriangles * layer + i 
                    linkIndex = nrTriangles * layer + neighbour
                    SetCellLink(index, linkIndex, LATERAL, exchangeArea)
        # DOWN
        for layer in range(nrLayers-1):
            exchangeArea = tin.C3DTIN[i].area
            index = nrTriangles * layer + i 
            linkIndex = index + nrTriangles
            SetCellLink(index, linkIndex, DOWN, exchangeArea)
    print("Initial water potential [m]:",C3DParameters.initialWaterPotential) 
    balance.initializeBalance()
    print("Initial water storage [m^3]:", balance.currentStep.waterStorage)
        
    print("Read precipitation data...")
    data, isFileOk = readDataFile(C3DParameters.precFileName, 1, "\t", False)
    if (not isFileOk):
        print("Error! Wrong precipitation file.") 
        return
    prec = data[:,1]
    nrObsPrec = len(prec)
    timeLength = C3DParameters.obsPrecTimeLength * 60   # [s]
    print("Time lenght [s]:", timeLength)
    print("Total simulation time [s]:", nrObsPrec * timeLength)
    
    visual3D.initialize(1280)
    visual3D.redraw(True)
    
    visual3D.isPause = True
    print("\nPress key (on a window):")
    print("'l' to load a saved state")
    print("'r' to start with initial conditions")
    while visual3D.isPause:
        visual3D.visual.wait()
    
    # main cycle
    for i in range(nrObsPrec):
        balance.currentPrec = prec[i] / timeLength * 3600
        setRainfall(prec[i], timeLength)
        compute(timeLength)
    
    visual3D.redraw(False)
    print ("\nEnd simulation.")      
main()

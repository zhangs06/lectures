#PSP_triangulation.py
from __future__ import print_function, division
from PSP_RamerDouglasPeucker import getDtmBoundary
from PSP_Delaunay import firstTriangulation
from PSP_refinement import *

def triangulate(header, dtm, quality, angleThreshold, isInitialPartition):             
    invQuality = 1.0 / quality 
    step = max(1, round(invQuality))    # [pixel] computation step  
    nrPixelsSide = sqrt(header.nrPixels)
    # [pixel] average distance between two points of the initial partition 
    partitionStep = round(invQuality * sqrt(nrPixelsSide))
    
    # [m] maximum height difference for refinement   
    thresholdZ = invQuality * header.dz / 100.0
    
    # [m] maximum perpendicular distance for boundary   
    thresholdRamer = thresholdZ * invQuality**2 
    
    #[m] maximum distance for boundary 
    maxBoundarySide = partitionStep * header.cellSize / 2.0
     
    # [m^2] minimum area of triangles
    minArea = invQuality * invQuality * header.cellSize**2
    
    # [0-1] fraction variability for partition 
    randomFactor = 0.3                

    pointList = getDtmBoundary(header, dtm, thresholdRamer, maxBoundarySide)
    flagMatrix = initializeFlagMatrix(header, dtm, pointList, step)
    
    visual3D.drawAllPoints(pointList, header)
     
    if isInitialPartition:    
        partitionPointList = addPartitionPoints(pointList, header, 
                  dtm, partitionStep, randomFactor, flagMatrix, step)
        visual3D.drawAllPoints(pointList, header)
    else:
        partitionPointList = []
        
    pointList = sortPointList(pointList)
    
    pointList, triangleList = firstTriangulation(pointList, partitionPointList, header, dtm)
    visual3D.drawAllTriangles(triangleList, header)
    
    pointList, triangleList, flagMatrix = refinementZ(pointList, triangleList, 
                        header, dtm, thresholdZ, minArea, flagMatrix, step)
    
    pointList, triangleList, flagMatrix = refinementAngle(pointList, triangleList, 
                        header, dtm, angleThreshold, minArea, flagMatrix, step)
    
    return (pointList, triangleList)

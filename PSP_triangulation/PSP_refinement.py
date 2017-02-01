#PSP_refinement.py
from __future__ import print_function, division
from PSP_Delaunay import insertVertexClockwise
import PSP_triangle as triangle
import PSP_visual3D as visual3D
from PSP_utility import *

REFINEMENTZ = 1
REFINEMENTANGLE = 2

def requireRefinement(header, dtm, flag, currentTriangle, zThreshold, step):
    plane = triangle.getPlane(currentTriangle.v)
    rect = triangle.getRectangle(currentTriangle.v)
    colMin, rowMin = getColRowFromXY(header, rect.x0, rect.y1)
    colMax, rowMax = getColRowFromXY(header, rect.x1, rect.y0)
    dzMax = 0.0
    for col in np.arange(colMin, colMax+1, step):
        for row in np.arange(rowMin, rowMax+1, step):
            if isTrue(header, flag, col, row):
                point = getPointFromColRow(header, dtm, col, row)
                if triangle.isPointInside(point, currentTriangle.v):
                    x, y, z = point
                    z0 = triangle.getZplane(plane, x, y)
                    dz = fabs(z - z0)
                    if (dz > dzMax): 
                        dzMax = dz
                        newRow = row
                        newCol = col    
    if (dzMax > zThreshold):
        return True, newCol, newRow
    else:
        return False, NODATA, NODATA 

    
def refinementZ(pointList, triangleList, header, dtm, zThreshold, areaMin, flagMatrix, step):
    print ("Z refinement...")
    triangleIndex = 0
    while triangleIndex < len(triangleList):
        currentTriangle = triangleList[triangleIndex] 
        refinementDone = False
        if not currentTriangle.isRefinedZ:
            if triangle.getArea2D(currentTriangle.v) > areaMin:
                required, newCol, newRow = requireRefinement(header, 
                                        dtm, flagMatrix, currentTriangle, zThreshold, step)
                if required:
                    newPoint = getPointFromColRow(header, dtm, newCol, newRow)
                    newTriangleIndex = refinement(triangleList, triangleIndex, newPoint, header, 
                                              dtm, REFINEMENTZ)
                    if newTriangleIndex != NODATA:
                        pointList.append(newPoint)
                        flagMatrix = updateFlagMatrix(flagMatrix, header, newCol, newRow, step)
                        triangleIndex = newTriangleIndex
                        refinementDone = True
                        
        triangleList[triangleIndex].isRefinedZ = True
        if (not refinementDone): triangleIndex += 1
        
    pointList = sortPointList(pointList)          
    return pointList, triangleList, flagMatrix

    
def refinementAngle(pointList, triangleList, header, dtm, angleThreshold, areaMin, flagMatrix, step):
    print ("angle refinement...")
    triangleIndex = 0
    while triangleIndex < len(triangleList):
        currentTriangle = triangleList[triangleIndex]
        refinementDone = False
        if not currentTriangle.isRefinedAngle:
            if triangle.getMinAngle(currentTriangle.v) < angleThreshold:
                if triangle.getArea2D(currentTriangle.v) > areaMin:
                    newCol, newRow = getColRowFromXY(header, 
                            currentTriangle.circle.x, currentTriangle.circle.y)
                    if isTrue(header, flagMatrix, newCol, newRow):
                        newPoint = getPointFromColRow(header, dtm, newCol, newRow)
                        newTriangleIndex = refinement(triangleList, triangleIndex, newPoint, 
                                         header, dtm, REFINEMENTANGLE)
                        if newTriangleIndex != NODATA:
                            pointList.append(newPoint)
                            flagMatrix = updateFlagMatrix(flagMatrix, header, newCol, newRow, step)
                            triangleIndex = newTriangleIndex
                            refinementDone = True
                            
        triangleList[triangleIndex].isRefinedAngle = True
        if (not refinementDone): triangleIndex += 1
        
    pointList = sortPointList(pointList)           
    return pointList, triangleList, flagMatrix

    
def refinement(triangleList, triangleIndex, newPoint, header, dtm, refinementType):
    deleteList = []
    vertexList = []
    angleList = []
    newTriangles = []
    checkList = []
    
    currentTriangle = triangleList[triangleIndex]
    if refinementType == REFINEMENTANGLE:
        isInside = triangle.isPointInside(newPoint, currentTriangle.v)
        
    deleteList.append(triangleIndex)
    for i in range(3):
        insertVertexClockwise(currentTriangle.v[i], 
                newPoint, vertexList, angleList)
    
    for i in range(len(triangleList)):
        if (i != triangleIndex): 
            myTriangle = triangleList[i]
            dx = newPoint[0] - myTriangle.circle.x
            if (dx <= myTriangle.circle.radius):
                dy = newPoint[1] - myTriangle.circle.y
                if (dy <= myTriangle.circle.radius):
                    if (((dx * dx) + (dy * dy)) <= myTriangle.circle.radiusSquared): 
                        checkList.append(i)         
    i = 0
    while (i < len(checkList)):                
        index = checkList[i]
        myTriangle = triangleList[index] 
        if  triangle.isAdjacent(myTriangle.v, vertexList):
            for j in range(3):
                insertVertexClockwise(myTriangle.v[j], 
                            newPoint, vertexList, angleList) 
            if refinementType == REFINEMENTANGLE and (not isInside):
                isInside = triangle.isPointInside(newPoint, myTriangle.v)
            orderedInsert(index, deleteList)
            checkList.pop(i)
            i = 0 
        else: i+=1 
            
    if refinementType == REFINEMENTANGLE and (not isInside): return NODATA 
    
    # create new triangles
    nrVertices = len(vertexList) 
    for i in range(nrVertices):
        v = np.zeros((3, 3), float)
        v[0] = newPoint
        v[1] = vertexList[i]
        v[2] = vertexList[(i+1) % nrVertices] 
        myTriangle = triangle.Ctriangle(v)
        if myTriangle.circle.isCorrect:
            newTriangles.append(myTriangle)
        else:
            return NODATA
    
    if len(newTriangles) <= len(deleteList): return NODATA
    
    firstIndex = deleteList[0]
    for i in range(len(deleteList)-1, -1, -1):
        triangleList.pop(deleteList[i])
        visual3D.delTriangle(deleteList[i])
    
    for i in range(len(newTriangles)):
        myTriangle = newTriangles[i]  
        triangleList.insert(firstIndex+i, myTriangle)
        visual3D.addTriangle(firstIndex+i, myTriangle, header)                       
    return firstIndex 

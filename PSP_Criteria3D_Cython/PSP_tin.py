#PSP_tin.py
from __future__ import print_function, division
from PSP_public import *
import numpy as np
from copy import copy

class CheaderTin():     
    xMin = NODATA  
    xMax = NODATA
    yMin = NODATA
    yMax = NODATA
    zMin = NODATA
    zMax = NODATA 
    dz = NODATA     
    magnify = NODATA
    
class Ctriangle:
    def __init__(self, v = np.zeros((3, 3), float)):
        self.isBoundary = False
        self.boundarySlope = NODATA
        self.boundarySide = NODATA
        self.v = copy(v)
        if (not np.all(v == 0.0)): 
            self.centroid = (v[0]+v[1]+v[2])/3.0
            self.area = getArea2D(self.v)

#global structures
header = CheaderTin()
C3DTIN = []

def magnitude(v):
    return(np.sqrt(v.dot(v)))

def getArea(v):
    return 0.5 * magnitude(np.cross(v[1] - v[0], v[2] - v[0]))

# Area = 1/2 |x1(y2-y3) - x2(y1-y3) + x3(y1 - y2)| 
def getArea2D(v):
    x = v[:,0]
    y = v[:,1]
    return 0.5 * fabs(x[0]*(y[1]-y[2]) - x[1]*(y[0]-y[2]) + x[2]*(y[0]-y[1]))

def getHeader(triangleList):
    header = CheaderTin()
    header.xMin = triangleList[0].centroid[0]
    header.yMin = triangleList[0].centroid[1]
    header.zMin = triangleList[0].centroid[2]
    header.xMax = header.xMin
    header.yMax = header.yMin
    header.zMax = header.zMin
    
    for i in range(1, len(triangleList)):
        x = triangleList[i].centroid[0]
        y = triangleList[i].centroid[1]
        z = triangleList[i].centroid[2]
        header.xMin = min(header.xMin, x)
        header.yMin = min(header.yMin, y)
        header.zMin = min(header.zMin, z)
        header.xMax = max(header.xMax, x)
        header.yMax = max(header.yMax, y)
        header.zMax = max(header.zMax, z)
        
    dx = header.xMax - header.xMin
    dy = header.yMax - header.yMin
    header.dz = header.zMax - header.zMin
    dtmRatio = (sqrt(dx*dy) / header.dz) * 0.1
    header.magnify = max(2.0, min(6.0, dtmRatio))
    return(header)
         
def distance2D(v1, v2):
    dx = fabs(v1[0] - v2[0])
    dy = fabs(v1[1] - v2[1])
    return sqrt(dx*dx + dy*dy)

def distance3D(v1, v2):
    dx = fabs(v1[0] - v2[0])
    dy = fabs(v1[1] - v2[1])
    dz = fabs(v1[2] - v2[2])
    return sqrt(dx*dx + dy*dy + dz*dz)

def getSlope(TIN, i, j):
    dz = TIN[i].centroid[2] - TIN[j].centroid[2]
    dxy = distance2D(TIN[i].centroid, TIN[j].centroid)
    return dz/dxy

def getBoundaryProperties(TIN, index, neighbours):
    slope = getSlope(TIN, int(neighbours[0]), index)
    if  (int(neighbours[1]) != NOLINK):
        slope1 = getSlope(TIN, int(neighbours[1]), index)
        slope = max(slope, slope1)
    TIN[index].boundarySlope = slope
    #TODO - migliorare 
    TIN[index].boundarySide = distance3D(TIN[index].v[0], TIN[index].v[1])        
        
def getAdjacentVertices(t1, t2):
    isFirst = True
    for i in range(3):
        for j in range(3):
            if (t1[i] == t2[j]):
                if isFirst:
                    index1 = t1[i]
                    isFirst = False
                else:
                    index2= t1[i]
                    return (index1, index2)
    return NOLINK, NOLINK

def getAdjacentSide(i, j, vertexList, triangleList):
    triangle1 = triangleList[i]
    triangle2 = triangleList[j]
    index1, index2 = getAdjacentVertices(triangle1, triangle2)
    v1 = vertexList[index1]
    v2 = vertexList[index2]
    return distance2D(v1, v2)     


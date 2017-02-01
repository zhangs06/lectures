#PSP_triangulation.py
from __future__ import print_function, division
from PSP_gis import *
     
def initializeFlagMatrix(header, dtm, pointList, step):
    flagMatrix = np.zeros((header.nrCols, header.nrRows), bool)
    
    for col in range(header.nrCols):
        for row in range(header.nrRows):
            if dtm[col][row] == header.flag:
                flagMatrix[col, row] = False
            else:
                flagMatrix[col, row] = True
                  
    for i in range(len(pointList)): 
        p = pointList[i]
        col, row = getColRowFromXY(header, p[0], p[1])   
        updateFlagMatrix(flagMatrix, header, col, row, step) 
    return flagMatrix
  
def updateFlagMatrix(flagMatrix, header, col, row, step):
    for dCol in np.arange(1-step, step):
        for dRow in np.arange(1-step, step):
            if not isOutOfGridColRow(header, col+dCol, row+dRow):
                flagMatrix[col+dCol, row+dRow] = False
    return flagMatrix

def searchPosition(x, sortPointList, first, last): 
    if x <= sortPointList[first][0]:
        return first
    elif x > sortPointList[last][0]:
        return (last+1)
    elif (last - first) < 2:
        return last
    else:
        m = int((first+last)/2)
        if (x <= sortPointList[m][0]):
            return(searchPosition(x, sortPointList, first, m))
        else:
            return(searchPosition(x, sortPointList, m, last)) 
                     
def sortPointList(pointList):
    sortList = [pointList[0]]
    for i in range(1, len(pointList)):
        x = pointList[i][0]
        index = searchPosition(x, sortList, 0, len(sortList) - 1)
        sortList.insert(index, pointList[i])
    return(sortList)                          

def addPartitionPoints(pointList, header, dtm, intervalStep, 
                       randomFactor, flagMatrix, flagStep):
    np.random.seed()
    col = 0
    isLastCol = False
    partitionPointList = []
    while not isLastCol:
        row = 0
        isLastRow = False
        while not isLastRow:
            delta = intervalStep * randomFactor * (2*np.random.random() - 1)
            c = col
            r = row
            if col != 0 and col < (header.nrCols -1): c += int(delta)
            if row != 0 and row < (header.nrRows -1): r += int(delta)
            if isTrue(header, flagMatrix, c, r): 
                point = getPointFromColRow(header, dtm, c, r)
                pointList.append(point)
                partitionPointList.append(point)
                flagMatrix = updateFlagMatrix(flagMatrix, header, c, r, flagStep)
            if (row == header.nrRows -1): 
                isLastRow = True
            else: 
                row += intervalStep
                if row >= (header.nrRows-intervalStep/3.): row = header.nrRows -1
        if (col == header.nrCols -1): 
            isLastCol = True
        else: 
            col += intervalStep
            if col >= (header.nrCols-intervalStep/3.): col = header.nrCols -1               
    return partitionPointList

def orderedInsert(index, indexList):
    #is first
    if (len(indexList) == 0):
        indexList.append(index)
        return()
    #check duplicate
    for i in range(len(indexList)):
        if (index == indexList[i]):
            return()
    #check position
    i = 0
    while ((i < len(indexList)) and (index > indexList[i])):
        i += 1
    indexList.insert(i, index)
    
def isAdjacentIndex(t1, t2):
    shareVertices = 0
    for i in range(3):
        for j in range(3):
            if (t1[i] == t2[j]):
                shareVertices += 1
                if shareVertices == 2:
                    return True
    return False
       
def getNeighbours(triangleList): 
    nrTriangles = len(triangleList)  
    neighbourList = np.zeros((nrTriangles, 3), int)
    nrNeighbours = np.zeros(nrTriangles, int)
    for i in range(nrTriangles):
        index = 0
        neighbourList[i] = [NOLINK, NOLINK, NOLINK]
        j = 0
        while (j < nrTriangles) and (index < 3):
            if (nrNeighbours[j]<3):
                if isAdjacentIndex(triangleList[i], triangleList[j]):
                    if (j != i):
                        neighbourList[i, index] = j
                        nrNeighbours[j] += 1
                        index += 1
            j += 1
    return(neighbourList)
    
def writeTIN(triangleList, pointList, header, dtm, 
             fnVertices, fnTriangles, fnNeighbours):
    print("Save TIN...")
    #save vertices
    file = open(fnVertices, "w")
    for i in range(len(pointList)):
        p = pointList[i]
        file.write(str(p[0]) +","+ str(p[1]) +","+ format(p[2],".1f") +"\n")
        
    #save triangle vertices
    triangleVertexList = np.zeros((len(triangleList),3), int)
    for i in range(len(triangleList)):
        for j in range(3):
            x = triangleList[i].v[j][0]
            pointIndex = searchPosition(x, pointList, 0, len(pointList)-1)
            while not(np.all(triangleList[i].v[j] == pointList[pointIndex])):
                pointIndex += 1
            triangleVertexList[i,j] = pointIndex
            
    file = open(fnTriangles, "w")
    for i in range(len(triangleVertexList)):
        t = triangleVertexList[i]
        file.write(str(t[0]) +","+ str(t[1]) +","+ str(t[2]) +"\n")
    
    neighbourList =  getNeighbours(triangleVertexList)
    file = open(fnNeighbours, "w")
    for i in range(len(neighbourList)):
        n = neighbourList[i]
        file.write(str(n[0]) +","+ str(n[1]) +","+ str(n[2]) +"\n")
            
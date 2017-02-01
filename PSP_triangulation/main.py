#PSP_triangulation
from __future__ import print_function, division

from PSP_triangulation import *
    
def main():
    #open DTM
    header, dtm = openDTM()
    pointListDTM = []
    for col in range(header.nrCols):
        for row in range(header.nrRows):
            if dtm[col, row]!= header.flag:
                p = getPointFromColRow(header, dtm, col, row)
                pointListDTM.append(p)
    header.nrPixels = len(pointListDTM)
    visual3D.initialize(header) 
    #visual3D.drawDTM(pointListDTM, header)
    print ("number of DTM points:", len(pointListDTM))

    #create TIN
    quality = 0.66                   # ]0, 1] refinement quality
    angleThreshold = pi/5.0          # [rad] minimum angle for refinement
    isInitialPartition = False       # initial regular subdivision choice    
    pointList, triangleList = triangulate(header, dtm, 
                        quality, angleThreshold, isInitialPartition)
    
    visual3D.drawAllSurfaces(triangleList, header)
    print ("number of triangles:", len(triangleList))
    
    #write TIN
    writeTIN(triangleList, pointList, header, dtm, 
             "vertices.csv", "triangles.csv", "neighbours.csv")
    print("End.")      
main()

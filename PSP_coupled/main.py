#PSP_coupled
from __future__ import print_function, division

import numpy as np
from PSP_public import *
import PSP_coupled1D as coupled
from PSP_soil import readSoil
from PSP_readDataFile import readDataFile
from PSP_plot import *
from PSP_longWaveRadiation import *
    
def main():
    isSuccess, mySoil = readSoil("soil.txt")
    if not isSuccess: 
        print("warning: wrong soil file.")
        return
    
    A, isFileOk = readDataFile('weather.dat', 1, '\t', False)
    if not isFileOk: 
        print ("Incorrect format in row: ", A)
        return()
    
    airT = A[:,1]
    prec = A[:,2]
    relativeHumidity = A[:,3]
    windSpeed = A[:,4]
    globalRadiation = A[:,6]
    longWaveRadiation = longWaveRadiationFromWeather(nrDays) 

    time = 0
    dt = 300
    sumWaterFlow = 0.
    sumHeatFlow = 0.  
    sumEvaporationFlow = 0.  
    nrIterations = 0
    
    coupled.initialize(mySoil, initialPotential, initialTemperature)
    plot_start(endTime)
    
    while (time < endTime):
        dt = min(dt, endTime - time)
        myBoundary = coupled.boundary.Cboundary()
        i = int(time/3600)
        myBoundary.time = time
        myBoundary.airTemperature = airT[i]
        myBoundary.precipitation = prec[i]
        myBoundary.relativeHumidity = relativeHumidity[i]
        myBoundary.windSpeed = windSpeed[i]
        myBoundary.globalRadiation = globalRadiation[i]
        myBoundary.longWaveRadiation = longWaveRadiation[i]

        (isBalanceOk, waterFlux, heatFlux, boundaryLayerConductance, evaporationFlux, 
		nrIterations,massBalance) = coupled.solver(mySoil, myBoundary, isFreeDrainage, dt)
 
        if isBalanceOk:
            for i in range(coupled.n+1):
                coupled.oldTheta[i] = coupled.theta[i]
                coupled.oldPsi[i] = coupled.psi[i]
                coupled.oldT[i] = coupled.T[i]
                coupled.oldCh[i] = coupled.Ch[i]
            sumWaterFlow += waterFlux * dt 
            sumHeatFlow += heatFlux * dt 
            sumEvaporationFlow += evaporationFlux * dt 
            time += dt
            print("time =", int(time), "\tdt =", dt, 
                  "\tnrIterations =", int(nrIterations), 
                  "\tsumWaterFlow:", format(sumWaterFlow, '.3f'), 
                  "\tsumHeatFlow:", format(sumHeatFlow,'.1f'))
            plot_variables(coupled.z, coupled.theta, coupled.T, coupled.psi, 
            time, boundaryLayerConductance, sumEvaporationFlow,
            myBoundary.precipitation, myBoundary.airTemperature,
            myBoundary.relativeHumidity)
            if (float(nrIterations / maxNrIterations) <= 0.1):  
                dt = int(min(dt*2, maxTimeStep))
                    
        else:
            print ("time =", int(time), "\tdt =", dt, "\tNo convergence")
            dt = max(int(dt / 2), 1)
            for i in range(coupled.n+1):
                coupled.theta[i] = coupled.oldTheta[i]
                coupled.psi[i] = coupled.oldPsi[i]
                coupled.T[i] = coupled.oldT[i]
    plot_end()
main()

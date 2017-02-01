#main.py
from __future__ import print_function, division
import matplotlib.pyplot as plt
from PSP_heat import *  
from PSP_grid import *

def main():  
    global z
    print (FIN_DIFF, 'Finite Difference')
    print (CELL_CENT_FIN_VOL, 'Cell-Centered Finite Volume')

    solver = int(input("Select solver: "))
    myStr = "water content (m^3/m^3): " 
    thetaIni = float(input(myStr))
    myStr = "mean temperature [C]: " 
    meanT = float(input(myStr))
    myStr = "amplitude of change in temperature [C]: " 
    ampT = float(input(myStr))
    omega = 2.0 * np.pi/(24 * 3600.0)
    airT0 = meanT
    timeShift = 8                       

    if (solver == FIN_DIFF):
        myStr = "weighting factor for time discretization:"
        myStr += " (0: explicit, 1: implicit Euler) = " 
        factor = float(input(myStr))
 
    z = initialize(airT0, thetaIni, solver)
    simulationLenght = int(input("nr of simulation hours: "))    
                    
    endTime = simulationLenght * 3600.0         
    timeStepMax = 3600.0                        
    dt = timeStepMax / 8.0                      
    time = 0.0                                  
    sumHeatFlux = 0
    totalIterationNr = 0
    
    f, plot = plt.subplots(3, figsize=(8,8), dpi=80)
    plt.subplots_adjust(hspace = 0.3)
    plot[1].set_xlabel("Time [h]",fontsize=14,labelpad=2)  
    plot[1].set_ylabel("Temperature [C]",fontsize=14,labelpad=4)
    plot[2].set_xlabel("Time [h]",fontsize=14,labelpad=2)
    plot[2].set_ylabel("Heat flux [W m$^{-2}$]",fontsize=14,labelpad=4)
    plot[1].set_xlim(timeShift, simulationLenght+timeShift)
    plot[1].set_ylim(meanT-ampT, meanT+ampT)
    plot[2].set_xlim(timeShift, simulationLenght+timeShift)
    
    while (time < endTime):
        dt = min(dt, endTime - time)
        airT = airT0 + ampT * np.sin((time+dt)*omega)
        if (solver == FIN_DIFF):
            success, nrIterations, heatFlux = (
                finiteDifference(airT, meanT, dt, factor))            
        elif (solver == CELL_CENT_FIN_VOL):
            success, nrIterations, heatFlux = (
                cellCentFiniteVol(airT, meanT, dt))
        totalIterationNr += nrIterations
        
        if success:
            #Convergence achieved
            for i in range(n+1):
                oldT[i] = T[i]
            sumHeatFlux += heatFlux * dt 
            time += dt
            
            t = time/3600. + timeShift
            
            plot[0].clear()
            plot[0].set_xlabel("Temperature [C]",fontsize=14,labelpad=2)
            plot[0].set_ylabel("Depth [m]",fontsize=14,labelpad=4) 
            plot[0].set_xlim(meanT-ampT, meanT+ampT) 
            plot[0].plot(T[1:len(T)], -z[1:len(T)], 'k')
            plot[0].plot(T[1:len(T)], -z[1:len(T)], 'ko')
            plot[1].plot(t, T[getLayerIndex(z, 0.0)], 'ko')    
            plot[1].plot(t, T[getLayerIndex(z, 0.05)], 'ks')     
            plot[1].plot(t, T[getLayerIndex(z, 0.2)], 'k^')    
            plot[2].plot(t, heatFlux, 'ko')
            plt.pause(0.0001)
            #increment time step when system is converging
            if (float(nrIterations/maxNrIterations) < 0.1): 
                dt = min(dt*2, timeStepMax)
        else:
            #No convergence
            dt = max(dt / 2, 1)
            for i in range(n+1): T[i] = oldT[i]
            print ("dt =", dt, "No convergence")
                    
    print("nr of iterations per hour:", totalIterationNr / simulationLenght)
    plt.ioff()
    plt.show()
main()

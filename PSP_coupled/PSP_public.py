#PSP_public.py
NODATA = -9999.

# Site
latitude = 44.5
longitude = 11.5
altitude = 120             
albedo = 0.2
atmPressure = 101.3
clay = 0.2

# Initial Condition
initialPotential = -1000.0
initialTemperature = 10.0     
isFreeDrainage = False

# Simulation 
area = 1                    
nrDays = 10                
endTime = 3600*24*nrDays   
toleranceVapour = 1.e-3     
toleranceHeat = 1.e-5      
maxNrIterations = 50.               
maxTimeStep = 3600.         

# Physics
L = 2.45e6                  
g = 9.8065                  
waterDensity = 1000.       
Mw = 0.018                  
R = 8.31                    
waterVapourDiff0 = 2.12E-5  
sigma = 5.67e-8             
heatCapacityWater = 4.18e3  
zeroKelvin = 273.15

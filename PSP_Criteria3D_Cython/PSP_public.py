#PSP_public.py
from math import sqrt, fabs, log

CAMPBELL = 1
IPPISCH_VG = 2

LOGARITHMIC = 0
HARMONIC = 1
GEOMETRIC = 2

# user choices
class C3DParameters:
    waterRetentionCurve = IPPISCH_VG
    meanType = LOGARITHMIC
    initialWaterPotential = -2.0            # [m]
    precFileName = "data/precipitation.txt"
    obsPrecTimeLength = 15                  # [minutes]
    computeOnlySurface = False
    isFreeDrainage = True
    minThickness = 0.01                        # [m]
    maxThickness = 0.1                      # [m]
    geometricFactor = 1.2
    roughness = 0.24                        # [s m^0.33]
    pond = 0.002                            # [m]
    currentDeltaT = 60.0                    # [s]
    deltaT_min = 6.0                        # [s]
    deltaT_max = obsPrecTimeLength * 60.0   # [s]
    maxIterationsNr = 100
    maxApproximationsNr = 10
    residualTolerance = 1E-12
    MBRThreshold = 1E-2
    conductivityHVRatio = 10.0

EPSILON_METER = 1E-5                        # [m]

UP = 1
DOWN = 2
LATERAL = 3

NODATA = -9999.
NOLINK = -1
        
BOUNDARY_RUNOFF = 1
BOUNDARY_FREEDRAINAGE = 2
BOUNDARY_FREELATERALDRAINAGE = 3
BOUNDARY_NONE = 99

OK = 1
INDEX_ERROR = -1111
LINK_ERROR = -5555

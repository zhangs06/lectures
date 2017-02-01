#PSP_longWaveRadiation
from __future__ import division
import numpy as np

albedo = 0.2
sigma = 5.670e-8  #[W/m2K4]
latitude = 46.73/360.*2.*3.1415 
M_w = 0.018
R = 8.31

def vaporConcentrationAir(T,relHum):  
    c_vsat = 0.611*1.e3*np.exp(17.27*T/(T+237.3)) * M_w/(R*(T+273.15))
    c_v = relHum*c_vsat
    return c_v

def atmEmissivity(measuredRadiation,day,T,relHum):
	sin_sD = (0.3985 * np.sin(4.869 + 0.0172*day + 0.03345*np.sin(6.224+0.0172*day)))  
	cos_sD = np.sqrt(1-sin_sD*sin_sD) 
	h_s = np.arccos(-np.tan(latitude)*(sin_sD/cos_sD))
	potentialRadiation = (117.5e6*(h_s*np.sin(latitude)*sin_sD
					+np.cos(latitude)*cos_sD*np.sin(h_s)) / 3.1415)
	T_t = measuredRadiation/potentialRadiation
	c_1 = 2.33-3.33*T_t
	if(c_1 < 0): 
		c_1 = 0.
	elif(c_1 > 1):
		c_1 = 1.
	c_va = vaporConcentrationAir(T,relHum)*1.e3  
	epsilon_a = 0.58*np.power(c_va,1./7.)
	emissivity = (1.-0.84*c_1)*epsilon_a + 0.84*c_1
	return emissivity

def longWaveRadiationFromWeather(nrDays):
	longWaveRadiation = np.zeros(nrDays*24)
	hour,temp,prec,hum,wvl,rad = (np.loadtxt('weather.dat',
	usecols=(0,1,2,3,4,6),unpack=True))
	for k in range(nrDays):
		dailyRad = sum(rad[k*24:(k+1)*24])*3600.
		for j in range(24):
			i = k*24+j
			longWaveRadiation[i] = (atmEmissivity(dailyRad,k,
			temp[i],hum[i]/100.)
			*sigma*np.power(temp[i]+273.15,4.))
	return longWaveRadiation
	
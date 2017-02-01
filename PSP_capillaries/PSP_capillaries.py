#PSP_capillaries.py
from visual import *
from math import sqrt
from numpy import *

def main():
	display(background=color.white)
	n = 250
	x = zeros(n)
	y = zeros(n)
	r = zeros(n)
	for i in range(n):
		check = 0
		while(check == 0):
			x[i] = random.random_sample()-0.5
			y[i] = random.random_sample()-0.5
			check = 1
			for j in range(i):
				if ((x[i]-x[j])**2.+(y[i]-y[j])**2.) < r[j]**2.:
					check = 0
			if not(x[i]*x[i]+y[i]*y[i]) < (0.2**2.): 
				check = 0
			r[i] = ((random.random_sample()*4.-2.)**2.+0.5)/4.*0.1
			for j in range(i):
				if ((x[i]-x[j])**2.+(y[i]-y[j])**2.) < (r[j]+r[i])**2.:
					r[i] = sqrt((x[i]-x[j])**2.+(y[i]-y[j])**2.)-r[j]
	for i in range(n):
		cylinder(pos=(x[i], y[i], -0.1), axis=(0,0,0.2), radius=r[i])
main()
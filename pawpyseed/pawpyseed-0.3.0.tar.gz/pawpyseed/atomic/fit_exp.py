import numpy as np 
from scipy.optimize import curve_fit
import matplotlib.pyplot as plt

def two_gauss(x, A, a, B, b):
	return A*np.exp(-a*x**2) + B*np.exp(-b*x**2)

x = np.linspace(0,10,500)
y = np.exp(-2*x)

popt, pcov = curve_fit(two_gauss, x, y, p0 = [1.2, 0.5, 0.3, 0.1])
print(popt,pcov)

plt.plot(x,y)
plt.plot(x,two_gauss(x, *popt))
plt.show()


import numpy as np 
import scipy.special
from scipy.misc import factorial as fac

def get_hwf(n,l):
	laguerre = scipy.special.genlaguerre(n-l-1, 2*l+1)
	scale = np.sqrt(8/n**3 * fac(n-l-1)/2/n/fac(n+1))
	def hwf(x):
		rho = 2*x/n
		return np.exp(-rho/2) * rho**l * laguerre(rho)
	return hwf

h1s = get_hwf(1,0)
h2s = get_hwf(2,0)
h2p = get_hwf(2,1)

x = np.linspace(0.0,25.0,10000,dtype=np.float64)
print(np.trapz(x*h1s(x)*h2s(x),x=x))
print(np.trapz(x*h1s(x)*h2p(x),x=x))

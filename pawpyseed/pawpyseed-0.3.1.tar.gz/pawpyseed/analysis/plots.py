import matplotlib.pyplot as plt 
import yaml


f = open('tst.txt', 'r')
myd = yaml.load(f)
f = myd['f']
yh = myd['yh']
r = myd['r']

plt.plot(f,yh)
plt.show()

plt.plot(r,f,label='f')
plt.plot(r,yh,label='y')
plt.legend()
plt.show()

plt.semilogx(r,f,label='f')
plt.semilogx(r,yh,label='y')
plt.legend()
plt.show()

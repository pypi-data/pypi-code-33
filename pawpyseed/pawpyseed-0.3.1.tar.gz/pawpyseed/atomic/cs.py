import numpy as np 
from sympy.physics.quantum.cg import CG
from sympy import S

def get_cg(l1, m1, l2, m2, l3, m3):
	cg = CG(S(l1), S(m1), S(l2), S(m2), S(l3), S(m3))
	return cg.doit()

f = open('condon_shortley.c', 'w')

f.write('#include "quadrature.h"\n\n')

MAXK = 8
MAXL = 4
f.write('double cg_coeff[%d][%d][%d][%d][%d] = ' % (MAXK+1, MAXL+1, MAXL+1, 2*MAXL+1, 2*MAXL+1))

cg_coeff = np.zeros((MAXK+1, MAXL+1, MAXL+1, 2*MAXL+1, 2*MAXL+1))

for k in range(9):
	for l1 in range(5):
		for l2 in range(5):
			for m1 in range(-l1,l1+1):
				for m2 in range(-l2,l2+1):
					coeff = ((2*l1+1)*(2*l2+1))**0.5 / (2*k+1) * (-1)**m2 * get_cg(l1, 0, l2, 0, k, 0) \
						* get_cg(l1, -m1, l2, m2, k, m2-m1)
					coeff = coeff.evalf()
					cg_coeff[k][l1][l2][m1+l1][m2+l2] = coeff

print (cg_coeff[2][1][1][1+1][1+1])
print (np.sqrt(np.sqrt(1/25)) / 5)
print (cg_coeff[2][1][1][1+1][1+0])
print (np.sqrt(3) / 5)
print (cg_coeff[2][1][1][1+0][1+0])
print (np.sqrt(4) / 5)
print (cg_coeff[2][1][1][1+1][1-1])
print (np.sqrt(6) / 5)
print (cg_coeff.tostring())
f.write((str(cg_coeff.tolist()).replace('[', '{').replace(']', '}')) + '\n\n')
f.close()



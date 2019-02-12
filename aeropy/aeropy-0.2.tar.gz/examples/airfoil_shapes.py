#!/usr/bin/python
# -*- coding: utf-8 -*-


"""
Example of the airfoil shape generator
"""


import numpy as np
import matplotlib.pyplot as plt
import aeropy.airfoils.shapes


# CST shape
coef_upper = np.array([0.1853, 0.0744, 0.2011, 0.1082, 0.3499])
coef_lower = np.array([-0.1986, -0.0459, -0.2527, -0.1783, 0.3355])
x, y = aeropy.airfoils.shapes.cst(coef_upper, coef_lower, 149)
plt.figure()
plt.title('CST (arbitrary) airfoil shape')
plt.xlabel('x')
plt.ylabel('y')
plt.plot(x, y)
plt.show()

# NACA shape
x, y = aeropy.airfoils.shapes.naca('2414', 149)
plt.figure()
plt.title('NACA2412 airfoil shape')
plt.xlabel('x')
plt.ylabel('y')
plt.plot(x, y)
plt.show()
#!/usr/bin/python
# -*- coding: utf-8 -*-


"""
Example of the airfoil analysis function. Please note that the SU2EDU function requires some computing time (several minutes).
"""


import numpy as np
import matplotlib.pyplot as plt
import aeropy.airfoils.shapes
import aeropy.airfoils.analysis


# The code needs to be wrapped in order to allow for safe multiprocessing
if __name__ == '__main__':

    # Set up airfoil and aoa range
    alphas = np.arange(0, 13, 3) * np.pi / 180.
    x, y = aeropy.airfoils.shapes.naca("2412", 149, half_cosine_spacing=True)

    boundary_x = np.array(x)[::-1]
    boundary_y = np.array(y)[::-1]
    # Calculate panel differences
    d_boundary_x = boundary_x[1:] - boundary_x[:-1]
    d_boundary_y = boundary_y[1:] - boundary_y[:-1]
    # Calculate panel lengths
    s = np.sqrt(d_boundary_x ** 2. + d_boundary_y ** 2.)
    # Calculate panel angles
    theta = np.arctan2(d_boundary_y, d_boundary_x)

    # Perform different analyses
    kuethecow_alphas, kuethecow_c_p, kuethecow_control_x, kuethecow_control_y, kuethecow_c_l, kuethecow_c_d = aeropy.airfoils.analysis.kuethecow(alphas, x, y)
    xfoil_alphas, xfoil_c_p, xfoil_control_x, xfoil_control_y, xfoil_c_l, xfoil_c_d = aeropy.airfoils.analysis.xfoil(alphas, x, y)
    su2edu_alphas, su2edu_c_p, su2edu_control_x, su2edu_control_y, su2edu_c_l, su2edu_c_d = aeropy.airfoils.analysis.su2edu(alphas, x, y, iterlim=200, cores=2)

    # Plot results
    plt.figure()
    plt.title("inviscid and incompressible example analysis of the naca2412 airfoil")
    plt.plot(xfoil_alphas * 180. / np.pi, xfoil_c_l, label="XFOIL")
    plt.plot(kuethecow_alphas * 180. / np.pi, kuethecow_c_l, label="Kuethe & Chow")
    plt.legend(loc="upper left")
    plt.ylabel("lift coefficient")
    plt.xlabel("alpha (in degree)")
    plt.show()

    plt.figure()
    plt.title("inviscid and compressible example analysis of the naca2412 airfoil")
    plt.plot(su2edu_alphas * 180. / np.pi, su2edu_c_l, label="SU2EDU")
    plt.legend(loc="upper left")
    plt.ylabel("lift coefficient")
    plt.xlabel("alpha (in degree)")
    plt.show()

    plt.figure()
    plt.title("inviscid and incompressible example analysis of the naca2412 airfoil")
    for i in range(len(alphas)):
        plt.plot(xfoil_control_x, xfoil_c_p[i], label="XFOIL " + str(xfoil_alphas[i] * 180. / np.pi) + " degree")
        plt.plot(kuethecow_control_x, kuethecow_c_p[i],
                 label="Kuethe & Chow " + str(kuethecow_alphas[i] * 180. / np.pi) + " degree")
    plt.legend()
    plt.gca().invert_yaxis()
    plt.ylabel("pressure coefficient")
    plt.xlabel("x")
    plt.show()

    plt.figure()
    plt.title("inviscid and compressible (M=0.3) example analysis of the naca2412 airfoil")
    for i in range(len(alphas)):
        plt.plot(su2edu_control_x, su2edu_c_p[i], label="SU2EDU " + str(su2edu_alphas[i] * 180. / np.pi) + " degree")
    plt.legend()
    plt.gca().invert_yaxis()
    plt.ylabel("pressure coefficient")
    plt.xlabel("x")
    plt.show()

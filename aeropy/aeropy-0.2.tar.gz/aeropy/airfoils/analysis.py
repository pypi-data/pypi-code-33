#!/usr/bin/python
# -*- coding: utf-8 -*-


"""
Python codes to analyse airfoil shapes
"""


from .executables.api import XFOIL, SU2EDU
from multiprocessing import Pool
from functools import partial

import numpy as np


def kuethecow(alphas, x, y):
    """
    Analyses an arbitrary airfoil shape based on a constant-strength
    vortex method as described in chapter 5 from Foundations of
    Aerodynamics by Kuethe & Chow
    """

    # SET UP GEOMETRY
    boundary_x = x
    boundary_y = y
    # Inverse arrays to allow clockwise rotation
    boundary_x = np.array(boundary_x)[::-1]
    boundary_y = np.array(boundary_y)[::-1]
    # Calculate control point (or singularity) coordinates
    control_x = (boundary_x[1:] + boundary_x[:-1]) / 2.
    control_y = (boundary_y[1:] + boundary_y[:-1]) / 2.
    # Calculate panel differences
    d_boundary_x = boundary_x[1:] - boundary_x[:-1]
    d_boundary_y = boundary_y[1:] - boundary_y[:-1]
    # Calculate panel lengths
    s = np.sqrt(d_boundary_x ** 2. + d_boundary_y ** 2.)
    # Calculate panel angles
    theta = np.arctan2(d_boundary_y, d_boundary_x)
    # Calculate number of panels
    n = len(theta)

    # SET UP SYSTEM OF EQUATIONS
    # Create meshgrid (for fast calculations)
    i, j = np.meshgrid(np.arange(n), np.arange(n), indexing='ij')
    # Calculate constants for the influence matix based on Kuethe & Chow
    convert_x = control_x[i] - boundary_x[j]
    convert_y = control_y[i] - boundary_y[j]
    A = -convert_x * np.cos(theta[j]) - convert_y * np.sin(theta[j])
    B = convert_x ** 2. + convert_y ** 2.
    convert_theta = theta[i] - theta[j]
    C = np.sin(convert_theta)
    D = np.cos(convert_theta)
    E = convert_x * np.sin(theta[j]) - convert_y * np.cos(theta[j])
    F = np.log(1. + (s[j] ** 2. + 2. * A * s[j]) / B)
    G = np.arctan2(E * s[j], B + A * s[j])
    P = convert_x * np.sin(theta[i] - 2. * theta[j]) + convert_y * np.cos(theta[i] - 2. * theta[j])
    Q = convert_x * np.cos(theta[i] - 2. * theta[j]) - convert_y * np.sin(theta[i] - 2. * theta[j])
    C_n2 = D + (0.5 * Q * F - (A * C + D * E) * G) / s[j]
    C_n1 = 0.5 * D * F + C * G - C_n2
    C_t2 = C + (0.5 * P * F + (A * D - C * E) * G) / s[j]
    C_t1 = 0.5 * C * F - D * G - C_t2
    np.fill_diagonal(C_n1, -1.0)  # self-induced normal velocity
    np.fill_diagonal(C_n2, 1.0)   # self-induced normal velocity
    np.fill_diagonal(C_t1, 0.5 * np.pi)
    np.fill_diagonal(C_t2, 0.5 * np.pi)
    # Calculate left hand side influence matrix
    A_n = np.empty([n + 1, n + 1])
    A_t = np.empty([n + 1, n + 1])
    for a in np.arange(n):
        A_n[a, 0] = C_n1[a, 0]  # normal velocity influence coefficients
        A_t[a, 0] = C_t1[a, 0]  # tangential velocity influence coefficients
        A_n[a, n] = C_n2[a, n - 1]  # normal velocity influence coefficients
        A_t[a, n] = C_t2[a, n - 1]  # tangential velocity influence coefficients
        for b in np.arange(1, n):
            A_n[a, b] = C_n1[a, b] + C_n2[a, b - 1]  # normal velocity influence coefficients
            A_t[a, b] = C_t1[a, b] + C_t2[a, b - 1]  # tangential velocity influence coefficients
    A_n[n, 0] = 1.  # Kutta condition
    A_n[n, n] = 1.  # Kutta condition
    for b in np.arange(1, n):
        A_n[n, b] = 0.  # Kutta condition

    # EVALUATE SYSTEM
    # Prepare outputs
    c_p = np.empty([len(alphas), n])
    c_l = np.empty(len(alphas))
    c_d = np.empty(len(alphas))
    # Loop over alphas
    for index in range(len(alphas)):
        # Get alpha
        alpha = alphas[index]
        # Calculate right hand side vector
        rhv = np.append(np.sin(theta - alpha), 0.)
        # Calculate vortex strength at the control points (per unit length)
        gamma = np.linalg.solve(A_n, rhv)
        # Calculate tangential velocity at the control points
        v = np.cos(theta - alpha) + np.sum(A_t * gamma, axis=1)[:-1]
        # Calculate pressure coefficient at the control points
        c_p[index] = 1.0 - v ** 2
        # Calculate total circulation, the factor 2 pi stems from the fact that gamma here in the code is actually
        # defined as gamma'=gamma/2piV
        #  Gamma = np.dot(gamma[:-1], s) * 2. * np.pi
        # Calculate the lift coefficient based on the Kutta-Joukowski theorem
        # This theoretical c_l will be discarded later, but it was used as verification during code development and
        # is thus still in the code
        #  c_l_theo = Gamma * 2
        # Calculate normal and tangential force coefficients
        c_n = np.dot(-c_p[index], d_boundary_x)
        c_t = np.dot(c_p[index], d_boundary_y)
        # Calculate lift coefficient and pressure drag coefficient
        c_l[index] = c_n * np.cos(alpha) - c_t * np.sin(alpha)
        c_d[index] = c_n * np.sin(alpha) + c_t * np.cos(alpha)
    # Return
    return alphas, c_p, control_x, control_y, c_l, c_d


def xfoil(alphas, x, y, GDES=False, flap=None, Re=None, Mach=None, Ncrit=None, xtr=None, iterlim=None,
                   NORM=True, commands=None):
    """
    Analyses an arbitrary airfoil shape with XFOIL based on codes from Pedro
    Leal & Hakan Tiftikci
    """

    # INITIALIZE XFOIL
    # Generate a new XFOIL instance
    xfoil = XFOIL()
    # Load airfoil coordinates into XFOIL and normalize
    xfoil.airfoil(x, y, NORM, GDES)
    # Configure XFOIL 
    if flap:
        xfoil.config.append("GDES")
        xfoil.config.append("FLAP")
        xfoil.config.append("%f" % flap[0])  # insert x location
        xfoil.config.append("%f" % flap[1])  # insert y location
        xfoil.config.append("%f" % flap[2])  # insesrt deflection in degrees
        xfoil.config.append("eXec")
        xfoil.config.append("")
    if True:
        xfoil.config.append("PLOP \n G \n")
        xfoil.config.append("OPER")
    if Ncrit:
        xfoil.config.append("vpar")
        xfoil.config.append("n %d" % Ncrit)
        xfoil.config.append("")
    if iterlim:
        xfoil.config.append("ITER {:.0f}".format(iterlim))
    if Re:
        xfoil.config.append("VISC {:.3f}".format(Re))
    if Mach:
        xfoil.config.append("MACH {:.3f} \n".format(Mach))
    if commands:
        xfoil.config.append(commands)

    # EXECUTE XFOIL
    xfoil.execute(alphas)

    # LOAD XFOIL DATA    
    # Get polar
    polar = xfoil.output_polar()
    try:
        alphas = polar[0][:, 0] / 180. * np.pi
        c_l = polar[0][:, 1]
        c_d = polar[0][:, 2]
    except:
        raise ValueError('XFOIL did not converge')
    # Get coordinates
    control_x, control_y = xfoil.output_coordinates()
    # Get pressure distributions    
    c_p = xfoil.output_pressures()
    # Return
    return alphas, c_p, control_x, control_y, c_l, c_d


def su2edu(alphas, x, y, cores=1, **kwargs):
    """
    Analyses an arbitrary airfoil shape with SU2EDU
    """

    # PREPARE MULTIPROCESSING
    pool = Pool(processes=cores)

    # EXECUTE MULTIPROCESSING     
    results = pool.map(partial(su2edu_base, x=x, y=y, **kwargs), alphas)

    # RETURN
    alphas = np.array([results[i][0] for i in range(len(results))])
    c_p = np.array([results[i][1] for i in range(len(results))])
    control_x = np.array(results[0][2])
    control_y = np.array(results[0][3])
    c_l = np.array([results[i][4] for i in range(len(results))])
    c_d = np.array([results[i][5] for i in range(len(results))])
    return alphas, c_p, control_x, control_y, c_l, c_d


def su2edu_base(alpha, x=None, y=None, Re=None, Mach=0.3, iterlim=150, turbulence='SST', temperature=288.15,
                pressure=101325.0):
    """
    Analyses an arbitrary airfoil shape with SU2EDU for a single alpha
    """

    # INITIALIZE SU2
    # Generate a new SU2 instance
    su2 = SU2EDU()
    # Load airfoil coordinates into SU2 
    su2.airfoil(x, y)
    # Configure SU2  
    if Re:
        # Viscid    
        su2.config.append('PHYSICAL_PROBLEM= NAVIER_STOKES')
        su2.config.append('KIND_TURB_MODEL= ' + turbulence)
        su2.config.append('REYNOLDS_NUMBER= ' + str(float(Re)))
        su2.config.append('CONV_NUM_METHOD_TURB= SCALAR_UPWIND-1ST_ORDER')
        su2.config.append('MARKER_HEATFLUX= ( airfoil, 0.0 )')
    else:
        # Inviscid
        su2.config.append('PHYSICAL_PROBLEM= EULER')
        su2.config.append('FREESTREAM_PRESSURE= ' + str(float(pressure)))
        su2.config.append('MARKER_EULER= ( airfoil )')
    su2.config.append('AoA= ' + str(float(alpha / np.pi * 180.)))
    su2.config.append('MACH_NUMBER= ' + str(float(Mach)))
    su2.config.append('FREESTREAM_TEMPERATURE= ' + str(float(temperature)))
    # Numerical method definiion    
    su2.config.append('CFL_NUMBER= 15.0')
    su2.config.append('CONV_NUM_METHOD_FLOW= ROE-2ND_ORDER')
    su2.config.append('EXT_ITER= ' + str(int(iterlim)))
    # Input and output definition
    su2.config.append('SOLUTION_FLOW_FILENAME= solution_flow.dat')
    su2.config.append('OUTPUT_FORMAT= PARAVIEW')
    su2.config.append('CONV_FILENAME= history')
    su2.config.append('RESTART_FLOW_FILENAME= restart_flow.dat')
    su2.config.append('VOLUME_FLOW_FILENAME= flow')
    su2.config.append('SURFACE_FLOW_FILENAME= surface_flow')
    su2.config.append('WRT_SOL_FREQ= 10')
    su2.config.append('WRT_CON_FREQ= 1')
    # Surface identification
    su2.config.append('MARKER_PLOTTING = ( airfoil )')
    su2.config.append('MARKER_MONITORING = ( airfoil )')
    su2.config.append('MARKER_MOVING= ( airfoil )')
    su2.config.append('MARKER_FAR= ( farfield )')

    # EXECUTE SU2
    su2.execute(Re)

    # LOAD SU2 DATA    
    # Get history
    history, history_header = su2.output_history()
    try:
        c_l = history[-1][1]
        c_d = history[-1][2]
    except:
        raise ValueError('SU2 did not converge')
    # Get surface
    surface, surface_header = su2.output_surface()
    control_x = surface[:, 1]
    control_y = surface[:, 2]
    #  p = surface[:, 3]
    c_p = surface[:, 4]
    additional = surface[:, 5]  # It's either the local Mach number (inviscid case)
                                # or the skin friction coefficient (viscid case)
    # Return
    return alpha, c_p, control_x, control_y, c_l, c_d, additional

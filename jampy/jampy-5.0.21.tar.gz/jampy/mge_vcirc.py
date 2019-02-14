"""
############################################################################

Copyright (C) 2003-2018, Michele Cappellari
E-mail: michele.cappellari_at_physics.ox.ac.uk

Updated versions of the software are available from my web page
http://purl.org/cappellari/software

If you have found this software useful for your research,
I would appreciate an acknowledgement to the use of the
"mge_vcirc routine in the Python modelling package jampy of Cappellari (2008)"

This software is provided as is without any warranty whatsoever.
Permission to use, for non-commercial purposes is granted.
Permission to modify for personal or internal use is granted,
provided this copyright and disclaimer are included unchanged
at the beginning of the file. All other rights are reserved.
In particular, redistribution of the code is not allowed.

############################################################################

Changelog
---------

V5.0.0: MC, Oxford, 19 December 2018
++++++++++++++++++++++++++++++++++++

- Formatted documentation as reStructuredText.
- Removed z dependence and simplified formalism.
- Vectorized integrand: significant speedup.

V4.0.2: MC, Oxford, 17 April 2018
+++++++++++++++++++++++++++++++++

- Changed imports for jampy as a package.
- Removed example. MC, Oxford, 17 April 2018

V4.0.1: MC, Oxford, 25 May 2014
+++++++++++++++++++++++++++++++

- Support both Python 2.7 and Python 3.

V4.0.0: MC, Oxford, 10 April 2014
+++++++++++++++++++++++++++++++++

- Translated from IDL into Python.

V3.0.2: MC, Windhoek, 1 October 2008
++++++++++++++++++++++++++++++++++++

- First released version. Included documentation. QUADVA integrator.

V3.0.0: MC, Leiden, 22 November 2005
++++++++++++++++++++++++++++++++++++

- Minor code polishing.

V3.0.0: MC, Oxford, 9 November 2006
+++++++++++++++++++++++++++++++++++

- This version retains only the few routines required for the
  computation of the circular velocity. All other unnecessary modelling
  routines have been removed.

V1.0.0: MC, Leiden, 3 February 2003
+++++++++++++++++++++++++++++++++++

- Written and tested by Michele Cappellari as part of the implementation of
  Schwarzschild's numerical orbit superposition method described in
  Cappellari et al. (2006, MNRAS).

"""

import numpy as np

from jampy.quadva import quadva

##############################################################################

def _integrand(u, r2, m, e2, s2):

    u2 = (u**2)[:, None]
    tmp = m*np.exp(-0.5*r2*u2/s2)*u2/np.sqrt(1. - e2*u2)

    return tmp.sum(1)

##############################################################################

def vcirc(R, dens, sigma, qintr, bhMass, soft):
    """
    Name
    ----

    MGE_VCIRC

    Purpose
    -------

    This procedure calculates the circular velocity in the equatorial plane of
    an axisymmetric galaxy model described by a Multi-Gaussian Expansion
    and a central black hole.

    This function evaluates the expression ``V_c = sqrt(R*D[pot, R])``, where the
    gravitational potential "pot" is given in eq. (16)-(18) of Cappellari (2008)

    Calling sequence
    ----------------

    .. code-block:: python

        from jampy.mge_vcirc import mge_vcirc

        vcirc = mge_vcirc(surf_pot, sigma_pot, qObs_pot,
                        inc_deg, mbh, distance, rad, vcirc, soft=0)

    Input parameters
    ----------------

    SURF_POT:
        vector of length M containing the peak value of the MGE Gaussians
        describing the galaxy surface density in units of Msun/pc**2 (solar
        masses per parsec**2). This is the MGE model from which the model
        potential is computed.
    SIGMA_POT:
        vector of length M containing the dispersion in arcseconds of
        the MGE Gaussians describing the galaxy surface density.
    QOBS_POT:
        vector of length M containing the observed axial ratio of the MGE
        Gaussians describing the galaxy surface density.
    INC_DEG:
        inclination in degrees (90 being edge-on).
    MBH:
        Mass of a nuclear supermassive black hole in solar masses.
    DISTANCE:
        distance of the galaxy in Mpc.
    RAD:
        Vector of length P with the radius in arcseconds, measured from the
        galaxy centre, at which one wants to compute the model predictions.

    Keywords
    --------

    SOFT:
        Softening length in arcsec for the Keplerian potential of the black
        hole. When this keyword is nonzero the black hole potential will be
        replaced by a Plummer potential with the given scale length.

    Output parameter
    ----------------

    VCIRC:
        Vector of length P with the model predictions for the circular
        velocity at the given input radii RAD.

    Required routines
    -----------------

        quadva by M. Cappellari (included in the JAM package):

    """

    e2 = 1. - qintr**2
    s2 = sigma**2
    r2 = R**2
    m = qintr*dens
    
    res = np.empty_like(r2)
    for j, r2j in enumerate(r2):
        res[j] = quadva(_integrand, [0., 1.], args=(r2j, m, e2, s2))[0]

    G = 0.00430237    # (km/s)**2 pc/Msun [6.674e-11 SI units (CODATA-14)]

    return R*np.sqrt(G*(4*np.pi*res + bhMass/(r2 + soft**2)**1.5))

##############################################################################

def mge_vcirc(surf_pc, sigma_arcsec, qobs, inc_deg, mbh, dist, rad, soft=0.):

    pc = dist*np.pi/0.648 # Constant factor to convert arcsec --> pc
    
    soft_pc = soft*pc           # Convert from arcsec to pc
    Rcirc = rad*pc              # Convert from arcsec to pc
    sigma = sigma_arcsec*pc     # Convert from arcsec to pc
    
    # Axisymmetric deprojection of total mass.
    # See equation (12)-(14) of Cappellari (2008, MNRAS)
    #
    inc = np.radians(inc_deg)
    qintr = qobs**2 - np.cos(inc)**2
    if np.any(qintr <= 0.0):
        raise ValueError('Inclination too low for deprojection')
    qintr = np.sqrt(qintr)/np.sin(inc)
    dens = surf_pc*qobs/(qintr*sigma*np.sqrt(2*np.pi))
    
    return vcirc(Rcirc, dens, sigma, qintr, mbh, soft_pc)

##############################################################################


import six
import os
import select
import sys
import stat
from functools import partial
from optparse import OptionParser, OptionGroup

import numpy as np
import time
import datetime

import lal
import lalsimulation as lalsim

import glue.lal
from glue.ligolw import utils, ligolw, lsctables, table, ilwd
lsctables.use_in(ligolw.LIGOLWContentHandler)
from glue.ligolw.utils import process
from glue import pipeline

#from pylal import series
from lal import series


from lalinference.rapid_pe import lalsimutils as lsu
from . import effectiveFisher as eff
from lalinference.rapid_pe import common_cl




def getSamples(
        mass1, mass2, chi1, network_snr,
        samples, psd_map,
        fmin=30, lowMass_fmin=None, highMass_fmin=None,
        NMcs=5, NEtas=5, NChis=5,
        mc_cut=1.741,
        lowMass_approx=lalsim.SpinTaylorT4, highMass_approx=lalsim.IMRPhenomPv2,
        Forced=False,
        random_state=None,
        deltaT=1./4096,
    ):
    """
    This function gives the samples from the 3D ambiguity ellipsoid around the
    triggered mass1, mass2 and chi1 value.

    Example of the function call:
    fisher_mat, samples = getSamples(
        10.0, 1.4, -0.5, 12.0,
        1000,
        {"H1": "../psds_2016.xml.gz", "L1": "../psds_2016.xml.gz"},
    )
    """

    # Set random state
    if random_state is None:
        random_state = np.random.RandomState()

    # Determine whether system has high (chirp) mass
    is_high_mass = lsu.mchirp(mass1, mass2) > mc_cut

    # Precompute SNR^2
    network_snr_sq = network_snr**2

    m1_SI = mass1 * lal.MSUN_SI
    m2_SI = mass2 * lal.MSUN_SI
#     min_mc_factor, max_mc_factor = 0.9, 1.1
    min_mc_factor, max_mc_factor = 0.98, 1.02
    if lsu.mchirp(mass1,mass2) > 15:
        min_mc_factor =0.8
        max_mc_factor =1.4
    min_eta, max_eta = 0.05, 0.25
    min_chi1, max_chi1 = -0.99, 0.99

    # match_cntr = 0.9 # Fill an ellipsoid of match = 0.9
    bank_min_match = 0.97
    # Bugfix? -DW
##    match_cntr = np.max([0.9, 1 - 9.2/2/network_snr_sq, bank_min_match])
##    wide_match = match_cntr
    match_cntr = 0.92 #inp.min([np.max([0.9, 1 - 9.2/2/network_snr_sq]), bank_min_match]) ## Richard's suggestion
#     wide_match = 1 - (1 - match_cntr)**(2/3.0)
    wide_match =  match_cntr # * 0.8 ### Richard's suggestion
    fit_cntr = match_cntr # Do the effective Fisher fit with pts above this match
    Nrandpts = samples # Requested number of pts to put inside the ellipsoid

    # Set fmin to mass-regime-specific value if provided otherwise use default: `fmin`
    fmin = (highMass_fmin if is_high_mass else lowMass_fmin) or fmin

    template_min_freq = fmin ### This needs to be discussed
    ip_min_freq = fmin ### This needs to be discussed
    lambda1, lambda2 = 0, 0

    #
    # Setup signal and IP class
    #
    param_names = ['Mc', 'eta', 'spin1z']
    McSIG = lsu.mchirp(m1_SI, m2_SI)
    etaSIG = lsu.symRatio(m1_SI, m2_SI)
    chiSIG = chi1

    if Forced or is_high_mass: ## If forced to use the IMR waveform, or if the chirp mass value is above the cut.
        PSIG = lsu.ChooseWaveformParams(
            m1=m1_SI, m2=m2_SI, spin1z=chi1, spin2z=chi1,
            lambda1=lambda1, lambda2=lambda2,
            fmin=template_min_freq,
            approx=highMass_approx,
            deltaT=deltaT
        )

    else:
        PSIG = lsu.ChooseWaveformParams(
            m1=m1_SI, m2=m2_SI, spin1z=chi1, spin2z=chi1,
            lambda1=lambda1, lambda2=lambda2,
            fmin=template_min_freq,
            approx=lowMass_approx,
            deltaT=deltaT
        )

    # Find a deltaF sufficient for entire range to be explored
    PTEST = PSIG.copy()

    # Check the waveform generated in the corners for the
    # longest possible waveform
    PTEST.m1, PTEST.m2 = lsu.m1m2(McSIG*min_mc_factor, min_eta)
    deltaF_1 = lsu.findDeltaF(PTEST)
    PTEST.m1, PTEST.m2 = lsu.m1m2(McSIG*min_mc_factor, max_eta)
    deltaF_2 = lsu.findDeltaF(PTEST)
    # set deltaF accordingly
    PSIG.deltaF = min(deltaF_1, deltaF_2)

    PTMPLT = PSIG.copy()

    for inst, psdfile in list(six.iteritems(psd_map)):
        if psd_map.has_key(psdfile):
            psd_map[psdfile].add(inst)
        else:
            psd_map[psdfile] = set([inst])
        del psd_map[inst]

    for psdf, insts in six.iteritems(psd_map):
        xmldoc = utils.load_filename(psdf, contenthandler=series.PSDContentHandler)
        # FIXME: How to handle multiple PSDs
        for inst in insts:
            psd = series.read_psd_xmldoc(xmldoc, root_name=None)[inst]
            psd_f_high = len(psd.data.data)*psd.deltaF
            f = np.arange(0, psd_f_high, psd.deltaF)
            fvals = np.arange(0, psd_f_high, PSIG.deltaF)
            eff_fisher_psd = np.interp(fvals, f, psd.data.data)

    analyticPSD_Q = False

    freq_upper_bound = np.min( [2000.0, (psd.data.length) * (psd.deltaF) * 0.98])

    IP = lsu.Overlap(fLow = ip_min_freq, fMax=freq_upper_bound,
        deltaF = PSIG.deltaF,
        psd = eff_fisher_psd,
        analyticPSD_Q = analyticPSD_Q
        )

    hfSIG = lsu.norm_hoff(PSIG, IP)

    # Find appropriate parameter ranges
    min_mc = McSIG * min_mc_factor
    max_mc = McSIG * max_mc_factor
    param_ranges = eff.find_effective_Fisher_region(PSIG, IP, wide_match,
            param_names, [[min_mc, max_mc],[min_eta, max_eta], [min_chi1, max_chi1]])


    # setup uniform parameter grid for effective Fisher
    pts_per_dim = [NMcs, NEtas, NChis]

    Mcpts, etapts, chipts = eff.make_regular_1d_grids(param_ranges, pts_per_dim)
    etapts = map(lsu.sanitize_eta, etapts)
    McMESH, etaMESH, chiMESH = eff.multi_dim_meshgrid(Mcpts, etapts, chipts)
    McFLAT, etaFLAT, chiFLAT = eff.multi_dim_flatgrid(Mcpts, etapts, chipts)
    dMcMESH = McMESH - McSIG
    detaMESH = etaMESH - etaSIG
    dchiMESH = chiMESH - chiSIG
    dMcFLAT = McFLAT - McSIG
    detaFLAT = etaFLAT - etaSIG
    dchiFLAT = chiFLAT - chiSIG

    grid = eff.multi_dim_grid(Mcpts, etapts, chipts)

    # Change units on Mc
    dMcFLAT_MSUN = dMcFLAT / lal.MSUN_SI
    dMcMESH_MSUN = dMcMESH / lal.MSUN_SI
    McMESH_MSUN = McMESH / lal.MSUN_SI
    McSIG_MSUN = McSIG / lal.MSUN_SI

    # Evaluate ambiguity function on the grid
    rhos = np.array(eff.evaluate_ip_on_grid(hfSIG, PTMPLT, IP, param_names, grid))
    rhogrid = rhos.reshape(NMcs, NEtas, NChis)

    # Fit to determine effective Fisher matrix
    # Adapt the match value to make sure all the Evals are positive

    # DW
##    gam_prior = np.diag([0.0, 4*4., 1.])
    gam_prior = np.diag([0.4*0.4, 4*4., 0.5*0.5]) # roughly 1 / (width of support)^2
##    gam_prior = np.diag([10.*10.,4*4.,1.])  # prior on mass, eta, chi.  (the 'prior' on mass is mainly used to regularize, and is too narrow)
    evals = np.array([-1, -1, -1])
    count = 0
    start = time.time()
    match_cntrs = np.array([0.98, 0.99, 0.995])
#    match_cntrs = np.array([0.97, 0.98, 0.99])
    while np.any(np.real(evals) < 0):
        fit_cntr = match_cntrs[count] # Do the effective Fisher fit with pts above this match
        cut = rhos > fit_cntr
        if np.sum(cut) >= 6:
            fitgamma = eff.effectiveFisher(
                eff.residuals3d,
                rhos[cut], dMcFLAT_MSUN[cut], detaFLAT[cut], dchiFLAT[cut],
            )
            # Find the eigenvalues/vectors of the effective Fisher matrix
            gam = eff.array_to_symmetric_matrix(fitgamma)
            gam = gam + gam_prior/network_snr_sq # holds in any coord system
            gam_backup = np.copy(gam)
            evals, evecs, rot = eff.eigensystem(gam)
            np.testing.assert_array_equal(gam_backup, gam)
            count += 1
            if (count >= 3) and np.any(np.real(evals) < 0):
                return gam * network_snr_sq, adapt_failure()
        else:
            return gam * network_snr_sq, adapt_failure()
    #
    # Distribute points inside predicted ellipsoid of certain level of overlap
    #
    r1 = np.sqrt(2.*(1.-match_cntr)/np.real(evals[0])) # ellipse radii ...
    r2 = np.sqrt(2.*(1.-match_cntr)/np.real(evals[1])) # ... along eigen-directions
    r3 = np.sqrt(2.*(1.-match_cntr)/np.real(evals[2])) # ... along eigen-directions
### CHECK ### Should we not use the updated match_cntr value? This seems to be a bug ###



    NN = 0
    NN_total = 0
    cart_grid = [[0., 0., 0.]]
    sph_grid = [[0., 0., 0.]]
    while NN < Nrandpts:
        NN_total += 1
        r = random_state.rand()
        ph = random_state.rand() * 2.*np.pi
        costh = random_state.rand()*2. - 1.
        sinth = np.sqrt(1. - costh * costh)
        th = np.arccos(costh)
        rrt = r**(1./3.)
        x1 = r1 * rrt * sinth * np.cos(ph)
        x2 = r2 * rrt * sinth * np.sin(ph)
        x3 = r3 * rrt * costh

        ### CHECK ####
        cart_grid_point = [x1, x2, x3]
        cart_grid_point = np.array(np.real( np.dot(rot, cart_grid_point)) )

        rand_Mc = cart_grid_point[0] * lal.MSUN_SI + McSIG # Mc (kg)
        rand_eta = cart_grid_point[1] + etaSIG # eta
        rand_chi = cart_grid_point[2] + chiSIG
        ### CHECK ####

        condition1 = rand_eta > 0
        condition2 = rand_eta <= 0.25
        condition3 = np.abs(rand_chi) < 1.0
        joint_condition = condition1 * condition2 * condition3
        if joint_condition:
            cart_grid.append( [cart_grid_point[0], cart_grid_point[1], cart_grid_point[2]] ) ## CHECK
            NN += 1
    cart_grid = np.array(cart_grid)
    sph_grid = np.array(sph_grid)

    # Rotate to get coordinates in parameter basis
    ### CHECK! No need to rotate again ###
#     cart_grid = np.array([ np.real( np.dot(rot, cart_grid[i]))
#         for i in xrange(len(cart_grid)) ])
    # Put in convenient units,
    # change from parameter differential (i.e. dtheta)
    # to absolute parameter value (i.e. theta = theta_true + dtheta)
    rand_dMcs_MSUN, rand_detas, rand_dChis = tuple(np.transpose(cart_grid)) # dMc, deta, dchi
    rand_Mcs = rand_dMcs_MSUN * lal.MSUN_SI + McSIG # Mc (kg)
    rand_etas = rand_detas + etaSIG # eta
    rand_chis = rand_dChis + chiSIG

    # Prune points with unphysical values of eta from cart_grid
    rand_etas = np.array(map(partial(lsu.sanitize_eta, exception=np.NAN), rand_etas))
    cart_grid = np.transpose((rand_Mcs,rand_etas,rand_chis)) #### CHECK ####
    phys_cut = ~np.isnan(cart_grid).any(1) # cut to remove unphysical pts
    cart_grid = cart_grid[phys_cut]
    keep_phys_spins = np.abs(cart_grid[:,2]) < 1.0 #### CHECK ####
    cart_grid = cart_grid[keep_phys_spins] #### CHECK ####

    # Output Cartesian and spherical coordinates of intrinsic grid
    indices = np.arange(len(cart_grid))
    Mcs_MSUN, etas, chis = np.transpose(cart_grid) #### CHECK ####
    Mcs_MSUN = Mcs_MSUN / lal.MSUN_SI
    outgrid = np.transpose((Mcs_MSUN,etas,chis)) #### CHECK ####

    return gam * network_snr_sq, outgrid



def adapt_failure():
    return np.array([np.nan, np.nan, np.nan])

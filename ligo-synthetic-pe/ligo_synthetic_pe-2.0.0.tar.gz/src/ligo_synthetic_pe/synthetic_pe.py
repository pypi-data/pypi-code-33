"""

"""
from __future__ import division, print_function

import numpy

import lal
import lalsimulation as lalsim
from lalinference.rapid_pe import lalsimutils as lsu

from glue.ligolw import utils
from lal import series

from . import fisher
from . import gw

def get_approximant_and_fmin(
        parameters,
        low_mass_fmin=30.0, high_mass_fmin=20.0,
        mchirp_threshold=1.741,
        low_mass_vacuum_approximant=lalsim.IMRPhenomD,
        high_mass_vacuum_approximant=lalsim.IMRPhenomPv2,
        matter_approximant=lalsim.IMRPhenomD_NRTidal,
    ):


    if (parameters.lambda1 != 0.0) or (parameters.lambda2 != 0.0):
        fmin = (
            high_mass_fmin if parameters.Mc_det > mchirp_threshold
            else low_mass_fmin
        )
        return matter_approximant, fmin

    if parameters.Mc_det > mchirp_threshold:
        return high_mass_vacuum_approximant, high_mass_fmin

    return low_mass_vacuum_approximant, low_mass_fmin


def fisher_cbc(
        coordinates, constants, parameters_center, network_snr,
        psd_file, instrument_name,
        wide_match=0.92,
        deltaT=1.0/4096.0,
    ):
    # Parameters at the central location in the given coordinate system.
    x_center = [getattr(parameters_center, coord) for coord in coordinates]

    # Precompute the square of the SNR.
    network_snr_sq = network_snr*network_snr

    # Determine the approximant and fmin according to the mass and whether/not
    # the binary is a vacuum solution (BBH) or not.
    approximant, fmin = get_approximant_and_fmin(parameters_center)

    # Ranges on eta and chirp mass
    min_eta, max_eta = 0.05, 0.25
    min_mc_factor, max_mc_factor = mc_factors(parameters_center)
    min_mc = min_mc_factor*parameters_center.Mc_det
    max_mc = max_mc_factor*parameters_center.Mc_det

    # Convert the parameters into the format lalsimutils (lsu) needs.
    lsu_params_center = lsu.ChooseWaveformParams(
        m1=parameters_center.m1_det*lal.MSUN_SI,
        m2=parameters_center.m2_det*lal.MSUN_SI,
        spin1z=parameters_center.chi1z, spin2z=parameters_center.chi2z,
        lambda1=parameters_center.lambda1, lambda2=parameters_center.lambda2,
        fmin=fmin, approx=approximant, deltaT=deltaT,
    )

    # Handle TD approximants.
    if lalsim.SimInspiralImplementedTDApproximants(approximant) == 1:
        ## Determine the deltaF to use based on the longest possible waveform.
        ## Note: will always use the low end of the chirp mass range, but vary
        ## the mass ratio.
        # Copy the params to avoid destroying data.
        lsu_params_test = lsu_params_center.copy()
        # Compute deltaF for the most extreme mass ratio.
        lsu_params_test.m1, lsu_params_test.m2 = lsu.m1m2(
            min_mc*lal.MSUN_SI, min_eta,
        )
        deltaF_min_eta = lsu.findDeltaF(lsu_params_test)
        # Compute deltaF for the most equal mass ratio.
        lsu_params_test.m1, lsu_params_test.m2 = lsu.m1m2(
            min_mc*lal.MSUN_SI, max_eta,
        )
        deltaF_max_eta = lsu.findDeltaF(lsu_params_test)
        # Smallest deltaF corresponds to longest waveform: use that.
        deltaF = min(deltaF_min_eta, deltaF_max_eta)
        lsu_params_center.deltaF = deltaF
        # Clear variables we no longer need.
        del lsu_params_test, deltaF_min_eta, deltaF_max_eta
    # Handle FD approximants.
    elif lalsim.SimInspiralImplementedFDApproximants(approximant) == 1:
        ## Determine the deltaF to use based on the longest possible waveform.
        ## Note: will always use the low end of the chirp mass range, but vary
        ## the mass ratio.
        # Copy the params to avoid destroying data.
        lsu_params_test = lsu_params_center.copy()
        # Compute duration for the most extreme mass ratio.
        lsu_params_test.m1, lsu_params_test.m2 = lsu.m1m2(
            min_mc*lal.MSUN_SI, min_eta,
        )
        duration_min_eta = lsu.estimateWaveformDuration(lsu_params_test)
        # Compute duration for the most equal mass ratio.
        lsu_params_test.m1, lsu_params_test.m2 = lsu.m1m2(
            min_mc*lal.MSUN_SI, max_eta,
        )
        duration_max_eta = lsu.estimateWaveformDuration(lsu_params_test)
        # Find the longest one.
        longest_duration = max(duration_min_eta, duration_max_eta)
        # deltaF = 1 / duration, but need to round up to the next power of 2
        # seconds.
        longest_duration = lsu.nextPow2(longest_duration)
        deltaF = 1.0 / longest_duration
        lsu_params_center.deltaF = deltaF
        # Clear variables we no longer need.
        del lsu_params_test
        del duration_min_eta, duration_max_eta, longest_duration
    # Error, appears neither to be TD or FD?  Should never occur.
    else:
        raise ValueError(
            "Approximant {} appears to have neither TD or FD support."
            .format(approximant)
        )


    # Make a copy of `lsu_params_center` that will be used at each of the points
    # in the test ellipsoid when computing the Fisher matrix.
    lsu_params_offcenter = lsu_params_center.copy()

    # Load in the PSD from a file.
    psd = load_psd(psd_file, instrument_name)

    # Construct an object for computing overlaps.
    overlap = construct_overlap(psd, fmin, deltaF)

    # Compute h(f) for the central parameters.
    strain_freq_center = lsu.norm_hoff(lsu_params_center, overlap)

    def compute_overlap(x):
        params_dict = constants.copy()
        for coord, xi in zip(coordinates, x):
            params_dict[coord] = xi

        parameters_offcenter = gw.CBCParameters(**params_dict)

        if parameters_offcenter.m1_det is not None:
            lsu_params_offcenter.m1 = parameters_offcenter.m1_det*lal.MSUN_SI
        if parameters_offcenter.m2_det is not None:
            lsu_params_offcenter.m2 = parameters_offcenter.m2_det*lal.MSUN_SI

        if parameters_offcenter.chi1z is not None:
            lsu_params_offcenter.spin1z = parameters_offcenter.chi1z
        if parameters_offcenter.chi2z is not None:
            lsu_params_offcenter.spin2z = parameters_offcenter.chi2z

        if parameters_offcenter.lambda1 is not None:
            lsu_params_offcenter.lambda1 = parameters_offcenter.lambda1
        if parameters_offcenter.lambda2 is not None:
            lsu_params_offcenter.lambda2 = parameters_offcenter.lambda2

        strain_freq_offcenter = lsu.norm_hoff(lsu_params_offcenter, overlap)

        return overlap.ip(strain_freq_center, strain_freq_offcenter)


    def in_domain(x):
        params_dict = constants.copy()
        for coord, xi in zip(coordinates, x):
            params_dict[coord] = xi

        parameters = gw.CBCParameters(**params_dict)

        return gw.valid_binary(parameters)


#    # TODO: Actually compute this based on the individual parameters.
#    radius = [0.1*getattr(parameters_center, coord) for coord in coordinates]
    parameter_ranges = compute_fisher_range(
        compute_overlap,
        coordinates, parameters_center, x_center,
        wide_match,
    )

    n_points = [
        gw.parameter_npoints.get(coordinate, 15)
        for coordinate in coordinates
    ]

    # Impose a weak prior on the Fisher matrix approximation to ensure the
    # covariance matrix is positive semi-definite.
    prior_inv_covar = numpy.diag([
        numpy.square(gw.parameter_priors[coord]) / network_snr_sq
        for coord in coordinates
    ])

    # Attempt to compute a working Fisher matrix
    match_thresholds = [0.98, 0.99, 0.995]
    for trial_number, match_threshold in enumerate(match_thresholds):
        fisher_object = fisher.Fisher.compute(
            compute_overlap, x_center, n_points,
            parameter_ranges=parameter_ranges,
            scale_factor=network_snr_sq,
            prior_inv_covar=prior_inv_covar,
            above_threshold=match_threshold,
            in_domain=in_domain,
        )

        if fisher_object.converged:
            return fisher_object

    raise ValueError(
        "Fisher matrix routine did not converge."
    )



def load_psd(psd_file, instrument_name):
    # Load the PSD file.
    xmldoc = utils.load_filename(
        psd_file, contenthandler=series.PSDContentHandler,
    )
    # Return the PSD just for the specified instrument.
    return series.read_psd_xmldoc(xmldoc, root_name=None)[instrument_name]


def construct_overlap(psd, fmin, deltaF):
    ## Interpolate the PSD from the file linearly, evaluating at the frequencies
    ## that will be needed for the inner product.
    # Maximum frequency we can evaluate the PSD at.
    psd_f_high = len(psd.data.data)*psd.deltaF
    # Frequencies the PSD was originally evaluated at.
    f = numpy.arange(0, psd_f_high, psd.deltaF)
    # Frequencies we need to evaluate the interpolant at.
    fvals = numpy.arange(0, psd_f_high, deltaF)
    # Evaluate the PSD at each point in `fvals`.
    eff_fisher_psd = numpy.interp(fvals, f, psd.data.data)

    freq_upper_bound = min(
        2000.0,
        psd.data.length * psd.deltaF * 0.98,
    )

    return lsu.Overlap(
        fLow=fmin, fMax=freq_upper_bound,
        deltaF=deltaF,
        psd=eff_fisher_psd,
        analyticPSD_Q=False,
    )


def mc_factors(parameters):
    """
    Determine relative width of chirp mass range to use.  Low mass binaries will
    have narrower chirp mass contours, so the values should be closer to unity,
    whereas high mass binaries will have wider ones, shifting the values away
    from unity.

    In principle these factors should be a function of the PSD, and should vary
    continuously according to the chirp mass.  One could do PE on a number of
    injections, and determine relative scales from that.  For the moment we just
    use hand-chosen numbers.
    """
    if parameters.Mc_det > 15.0:
        min_mc_factor, max_mc_factor = 0.8, 1.4
    else:
        min_mc_factor, max_mc_factor = 0.98, 1.02

    return min_mc_factor, max_mc_factor


def parameter_range(coordinate, parameters):
    if coordinate == "Mc_det":
        mc_min_factor, mc_max_factor = mc_factors(parameters)
        return parameters.Mc_det*mc_min_factor, parameters.Mc_det*mc_max_factor

    if coordinate == "eta":
        return 0.05, 0.25

    if (coordinate == "chi1z") or (coordinate == "chi2z"):
        return -0.99, +0.99

    if (coordinate == "lambda1") or (coordinate == "lambda2"):
        return 0.0, 1500.0

    raise NotImplementedError(
        "Still need to implement range for '{}'.".format(coordinate)
    )



def compute_fisher_range(
        overlap_fn,
        coordinates, parameters_center, x_center,
        target_match,
        tolerance=1.0e-6
    ):
    import scipy.optimize

    ranges = []
    for index, coordinate in enumerate(coordinates):
        parameter_center = x_center[index]
        x_center_copy = list(x_center)
        range_lo, range_hi = parameter_range(coordinate, parameters_center)

        def func(parameter):
            x_center_copy[index] = parameter

            return overlap_fn(x_center_copy) - target_match

        try:
            range_lo_computed = scipy.optimize.brentq(
                func,
                range_lo, parameter_center,
                xtol=tolerance,
            )
        except ValueError:
            range_lo_computed = range_lo

        try:
            range_hi_computed = scipy.optimize.brentq(
                func,
                parameter_center, range_hi,
                xtol=tolerance,
            )
        except ValueError:
            range_hi_computed = range_hi

        ranges.append((range_lo_computed, range_hi_computed))

    return ranges


def get_samples(
        m1, m2, chi1xyz, chi2xyz, network_snr,
        n_samples, psd_map,
        n_samples_fisher=1000,
        burnin=2000, acorr=40, walkers=40,
        m_min=None, m_max=None, M_max=None,
        threads=None,
        no_shift=False,
        full_chain_hdf5=None,
        random_state=None,
    ):
    import numpy

    from .EM_Bright import getEllipsoidSamples
    from . import gw, spin_samplers, utils

    chi1x, chi1y, chi1z = chi1xyz
    chi2x, chi2y, chi2z = chi2xyz

    M = m1 + m2
    eta = gw.symmetric_mass_ratio(m1, m2, M=M)
    mc = gw.chirp_mass(M, eta)
    chi_eff = gw.effective_inspiral_spin(
        m1, m2,
        chi1z, chi2z,
        M=M,
    )

    # Compute Fisher matrix, and covariance matrix (its inverse)
    fisher_mc_eta_chieff, _ = getEllipsoidSamples.getSamples(
        m1, m2, chi_eff, network_snr,
        n_samples_fisher, psd_map,
        lowMass_fmin=30.0, highMass_fmin=20.0,
        NMcs=10, NEtas=10, NChis=10,
        random_state=random_state,
    )
    covar_mc_eta_chieff = numpy.linalg.inv(fisher_mc_eta_chieff)


    mean_mc_eta_chieff = [mc, eta, chi_eff]

    # (Skip if `no_shift=True`, in which case we keep 'true' mean)
    # Determine the new mean vector by taking one draw from the Fisher matrix,
    # without using the (Mc,eta,chi) prior, and without restricting the range to
    # valid values of mass and spin. The tails of the distribution will still
    # extend to valid values, so it will be well defined.
    if not no_shift:
        mean_mc_eta_chieff = random_state.multivariate_normal(
            mean_mc_eta_chieff, covar_mc_eta_chieff,
        )

    '''
    mean_mc_eta_chi12xyz = sample_fisher(
        1,
        burnin, acorr, walkers,
        [mc, eta, chi_eff], covar_mc_eta_chieff,
        threads=threads,
        random_state=random_state,
    )

    # Extract the components of the new mean vector that matter. We're going to
    # carry over mc,eta, and then use chi{1,2}z to compute chi_eff.
    mean_mc = mean_mc_eta_chi12xyz[0,0]
    mean_eta = mean_mc_eta_chi12xyz[0,1]
    mean_chi1z = mean_mc_eta_chi12xyz[0,4]
    mean_chi2z = mean_mc_eta_chi12xyz[0,7]

    # Convert mc,eta to m1,m2 so we can compute chi_eff.
    mean_m1, mean_m2 = gw.mc_eta_2_m1_m2(mean_mc, mean_eta)

    # Compute the chi_eff corresponding to the mean vector we have.
    mean_chieff = gw.effective_inspiral_spin(
        mean_m1, mean_m2, mean_chi1z, mean_chi2z,
    )
    '''

    # Draw the final samples in (mc, eta, chi{1,2}{x,y,z}) coordinates.
    return sample_fisher(
        n_samples,
        burnin, acorr, walkers,
        mean_mc_eta_chieff, covar_mc_eta_chieff,
        m_min=m_min, m_max=m_max, M_max=M_max,
        threads=threads,
        full_chain_hdf5=full_chain_hdf5,
        random_state=random_state,
    )


def sample_fisher(
        n_samples,
        burnin, acorr, walkers,
        mean, cov,
        m_min=None, m_max=None, M_max=None,
        init_state=None,
        threads=None,
        full_chain_hdf5=None,
        random_state=None,
    ):
    import numpy
    import scipy.stats
    import emcee

    from .utils import sample_gaussian_mc_eta_chieff

    if full_chain_hdf5 is not None:
        import h5py

    # 2 mass dimensions, 6 spin dimensions
    ndim = 8

    samples_per_walker = int(numpy.ceil(n_samples/walkers))

    # Gaussian in mc, eta, chi_eff
    gaussian = scipy.stats.multivariate_normal(mean, cov)


    if init_state is None:
        init_state_mc_eta_chieff = sample_gaussian_mc_eta_chieff(
            walkers, mean, cov,
            random_state=random_state,
            m_min=m_min, m_max=m_max, M_max=M_max,
        )

        init_state = numpy.zeros((walkers, ndim), dtype=numpy.float64)

        # Use mc, eta from the Fisher matrix draw as is
        init_state[:,0] = init_state_mc_eta_chieff[:,0]
        init_state[:,1] = init_state_mc_eta_chieff[:,1]

        # Use chi_eff from the Fisher matrix draw for both chi1z, chi2z, and
        # then add a Gaussian perturbation
        init_state[:,4] = init_state_mc_eta_chieff[:,2]
        init_state[:,4] += random_state.normal(0.0, 0.05, size=walkers)
        init_state[:,7] = init_state_mc_eta_chieff[:,2]
        init_state[:,7] += random_state.normal(0.0, 0.05, size=walkers)

        # Leave chi{1,2}{x,y} approximately 0
        # Can't have exactly zero or will get log(0) in the prior
        init_state[:,2:4] = random_state.uniform(-0.1, +0.1, size=(walkers, 2))
        init_state[:,5:7] = random_state.uniform(-0.1, +0.1, size=(walkers, 2))

        del init_state_mc_eta_chieff


    sampler = emcee.EnsembleSampler(
        walkers, ndim,
        _ln_post,
        threads=threads,
        args=[gaussian, m_min, m_max, M_max],
    )

    # Run the sampler through burnin
    init_state_post_burnin, _, _ = sampler.run_mcmc(
        init_state, burnin,
        storechain=False,
        rstate0=random_state,
    )
    sampler.reset()

    # Draw the actual samples.
    sampler.run_mcmc(
        init_state_post_burnin, samples_per_walker*acorr,
        storechain=True,
        rstate0=random_state,
    )

    if full_chain_hdf5 is not None:
        with h5py.File(full_chain_hdf5, "w") as hdf5_file:
            hdf5_file.create_dataset(
                "chains",
                data=sampler.chain,
            )
            hdf5_file.create_dataset(
                "log_prob",
                data=sampler.lnprobability,
            )

    # Remove autocorrelation from chain
    return sampler.chain[:,::acorr].reshape((-1, ndim))[:n_samples]


def _ln_post(mc_eta_chi12xyz, gaussian, m_min, m_max, M_max):
    import numpy
    from . import gw
    from .utils import valid_mc_eta_chi12xyz

    mc, eta, chi1x, chi1y, chi1z, chi2x, chi2y, chi2z = mc_eta_chi12xyz

    is_valid = valid_mc_eta_chi12xyz(
        mc, eta, chi1x, chi1y, chi1z, chi2x, chi2y, chi2z,
        m_min=m_min, m_max=m_max, M_max=M_max,
    )
    if not is_valid:
        return -numpy.inf

    ln_pi = gw.uniform_mass_mc_eta_log_prior(mc, eta)
    ln_pi += gw.uniform_spin_mag_log_prior(chi1x, chi1y, chi1z)
    ln_pi += gw.uniform_spin_mag_log_prior(chi2x, chi2y, chi2z)

    if not numpy.isfinite(ln_pi):
        return ln_pi

    m1, m2 = gw.mc_eta_2_m1_m2(mc, eta)
    chi_eff = gw.effective_inspiral_spin(m1, m2, chi1z, chi2z)

    ln_like = gaussian.logpdf([mc, eta, chi_eff])

    return ln_pi + ln_like

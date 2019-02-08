"""

"""
from __future__ import division, print_function


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

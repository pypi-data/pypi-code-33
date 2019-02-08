from __future__ import division


def isotropic_uniform_spin_mag_sampler(
        n_samples,
        chi_max=1.0,
        random_state=None,
    ):
    import numpy

    if random_state is None:
        random_state = numpy.random.RandomState()


    chi1 = random_state.uniform(0.0, chi_max, n_samples)
    chi2 = random_state.uniform(0.0, chi_max, n_samples)

    costh1 = random_state.uniform(-1.0, +1.0, n_samples)
    costh2 = random_state.uniform(-1.0, +1.0, n_samples)

    phi1 = random_state.uniform(0.0, 2.0*numpy.pi, n_samples)
    phi2 = random_state.uniform(0.0, 2.0*numpy.pi, n_samples)


    sinth1 = numpy.sin(numpy.arccos(costh1))
    sinth2 = numpy.sin(numpy.arccos(costh2))


    out = numpy.empty((n_samples, 6), dtype=numpy.float64)

    out[:,0] = chi1 * sinth1 * numpy.cos(phi1)
    out[:,1] = chi1 * sinth1 * numpy.sin(phi1)
    out[:,2] = chi1 * costh1

    out[:,3] = chi2 * sinth2 * numpy.cos(phi2)
    out[:,4] = chi2 * sinth2 * numpy.sin(phi2)
    out[:,5] = chi2 * costh2

    return out


def volumetric_sampler(
        n_samples,
        chi_max=1.0,
        random_state=None,
    ):
    raise NotImplementedError

from __future__ import division


def sample_gaussian_mc_eta_chieff(
        n_samples,
        mean, cov,
        random_state=None,
        **validation_kwargs
    ):
    import numpy

    if random_state is None:
        random_state = numpy.random.RandomState()

    def draw():
        return random_state.multivariate_normal(mean, cov)

    out = numpy.empty((n_samples, 3), dtype=numpy.float64)

    n_drawn = 0
    while n_drawn < n_samples:
        candidate = draw()

        if valid_mc_eta_chieff(*candidate, **validation_kwargs):
            out[n_drawn] = candidate
            n_drawn += 1

    return out



def valid_mc_eta_chieff(
        mc, eta, chi_eff,
        m_min=None, m_max=None, M_max=None,
    ):
    from . import gw

    if mc <= 0.0:
        return  False

    if (eta <= 0) or (eta > 0.25):
        return False

    if (chi_eff < -1.0) or (chi_eff > +1.0):
        return False

    if any(x is not None for x in [m_min, m_max, M_max]):
        m_1, m_2 = gw.mc_eta_2_m1_m2(mc, eta)

        if (m_min is not None) and (m_2 < m_min):
            return False
        if (m_max is not None) and (m_1 > m_max):
            return False
        if (M_max is not None) and (m_1 + m_2 > M_max):
            return False

    return True


def valid_mc_eta_chi1z_chi2z(
        mc, eta, chi1z, chi2z,
        m_min=None, m_max=None, M_max=None,
    ):
    from . import gw

    if mc <= 0.0:
        return  False

    if (eta <= 0) or (eta > 0.25):
        return False

    if (chi1z < -1.0) or (chi1z > +1.0):
        return False

    if (chi2z < -1.0) or (chi2z > +1.0):
        return False

    if any(x is not None for x in [m_min, m_max, M_max]):
        m_1, m_2 = gw.mc_eta_2_m1_m2(mc, eta)

        if (m_min is not None) and (m_2 < m_min):
            return False
        if (m_max is not None) and (m_1 > m_max):
            return False
        if (M_max is not None) and (m_1 + m_2 > M_max):
            return False

    return True


def valid_mc_eta_chi12xyz(mc, eta, *chi12xyz, **kwargs):
    from . import gw

    import numpy


    # Ensure mass is positive.
    if mc <= 0.0:
        return  False

    # Ensure mass ratio is valid.
    if (eta <= 0) or (eta > 0.25):
        return False

    # Ensure spin components are on [-1, +1].
    for chi in chi12xyz:
        if (chi < -1.0) or (chi > +1.0):
            return False

    # Ensure spin magnitude isn't greater than 1.
    for chixyz in [chi12xyz[:3], chi12xyz[3:]]:
        if numpy.linalg.norm(chixyz) > 1.0:
            return False


    m_min = kwargs.get("m_min")
    m_max = kwargs.get("m_max")
    M_max = kwargs.get("M_max")
    if any(x is not None for x in [m_min, m_max, M_max]):
        m_1, m_2 = gw.mc_eta_2_m1_m2(mc, eta)

        if (m_min is not None) and (m_2 < m_min):
            return False
        if (m_max is not None) and (m_1 > m_max):
            return False
        if (M_max is not None) and (m_1 + m_2 > M_max):
            return False

    # Checks out
    return True

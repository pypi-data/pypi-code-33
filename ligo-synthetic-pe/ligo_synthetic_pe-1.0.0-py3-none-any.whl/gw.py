from __future__ import division


_FIVE_THIRDS  = 5.0 / 3.0
_EIGHT_THIRDS = 8.0 / 3.0
_THREE_FIFTHS = 3.0 / 5.0


def symmetric_mass_ratio(m_1, m_2, M=None):
    """
    Compute the symmetric mass ratio, ``eta``, given the component masses,
    ``m_1`` and ``m_2``. Can optionally provide the total mass, ``M``, to save
    re-computing it with ``M = m_1 + m_2``.

    **Parameters**

    m_1: array-like, shape = S
        The mass of the first binary object.

    m_2: array-like, shape = S
        The mass of the second binary object.

    M: array-like, shape = S (optional)
        The total mass of the binary.

    **Returns**

    eta: array-like, shape = S
        The symmetric mass ratio of the binary.
    """
    if M is None:
        M = m_1 + m_2

    return m_1 * m_2 * M**-2


def chirp_mass(M, eta):
    """
    Compute the chirp mass, ``M_c``, given the total mass ``M`` and the
    symmetric mass ratio ``eta``.

    **Parameters**

    M: array-like, shape = S
        The total mass of the binary.

    eta: array-like, shape = S
        The symmetric mass ratio of the binary.

    **Returns**

    M_c: array-like, shape = S
        The chirp mass of the binary.
    """
    return eta**_THREE_FIFTHS * M


def mc_eta_2_m1_m2(M_c, eta):
    r"""
    Computes the component masses, ``(m_1, m_2)``, from the chirp mass ``M_c``
    and the symmetric mass ratio ``eta``. Uses the conversion formula:

    .. math::

        x = \max(1 - 4*\eta, 0)
        y = \frac{ \mathcal{M}_c }{ 2 * \eta^{3/5} }

        m_1 = y \cdot (1 + \sqrt(x))
        m_2 = y \cdot (1 - \sqrt(x))

    **Parameters**

    M_c: array-like, shape = S
        The chirp mass of the binary.

    eta: array-like, shape = S
        The symmetric mass ratio of the binary.

    **Returns**

    m_1: array-like, shape = S
        The mass of the first binary object.

    m_2: array-like, shape = S
        The mass of the second binary object.
    """
    import numpy

    x = numpy.maximum(1 - 4*eta, 0.0)
    sqrtx = numpy.sqrt(x)

    # Temporary value of m_1. Multiplication by 1+sqrtx comes later
    m_1 = 0.5 * M_c * eta**-0.6

    m_2 = m_1 * (1.0 - sqrtx)
    m_1 *= 1.0 + sqrtx

    return m_1, m_2


def effective_inspiral_spin(m1, m2, chi1z, chi2z, M=None):
    if M is None:
        M = m1 + m2

    return (m1*chi1z + m2*chi2z) / M


def uniform_mass_mc_eta_log_prior(M_c, eta):
    r"""
    If :math:`p(m_1, m_2)` is unformly distributed (subject to
    :math:`m_i \geq m_{\mathrm{min}}` and
    :math:`m_1 + m_2 \leq M_{\mathrm{max}}`), then that implies

    .. math::
       p(\mathcal{M}_{\mathrm{c}}, \eta) =
       \frac{4}{(M_{\mathrm{max}} - m_{\mathrm{min}})^2}
       \frac{\mathcal{M}_{\mathrm{c}}}{\eta^{6/5} \sqrt{1 - 4\eta}}

    This evaluates that function, in the log, neglecting the constant factor
    dealing with the lower and upper mass cutoffs.
    """
    import numpy

    return numpy.log(M_c) - 1.2*numpy.log(eta) - 0.5*numpy.log(1.0 - 4.0*eta)


def uniform_spin_mag_log_prior(chix, chiy, chiz):
    import numpy

    chi = numpy.linalg.norm([chix, chiy, chiz])

    return -2.0 * numpy.log(chi)


def aligned_z_log_prior(chiz, chi_max):
    import numpy

    return numpy.log(-numpy.log(numpy.abs(chiz / chi_max)))

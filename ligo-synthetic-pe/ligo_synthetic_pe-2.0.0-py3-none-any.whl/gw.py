from __future__ import division

import numpy

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


class CBCParameters(object):
    def __init__(
            self,
            m1_source=None, m1_det=None,
            m2_source=None, m2_det=None,
            M_source=None, M_det=None,
            Mc_source=None, Mc_det=None,
            eta=None, q=None,
            chi1=None, chi2=None,
            chi1x=None, chi1y=None, chi1z=None,
            chi2x=None, chi2y=None, chi2z=None,
            cos_tilt1=None, cos_tilt2=None,
            phi1=None, phi2=None,
            chi_eff=None,
            z=None,
            lambda1=None, lambda2=None, lambda_tilde=None,
        ):
        self.m1_source = m1_source
        self.m1_det = m1_det

        self.m2_source = m2_source
        self.m2_det = m2_det

        self.M_source = M_source
        self.M_det = M_det

        self.Mc_source = Mc_source
        self.Mc_det = Mc_det

        self.eta = eta
        self.q = q

        self.chi1 = chi1
        self.chi2 = chi2

        self.chi1x = chi1x
        self.chi1y = chi1y
        self.chi1z = chi1z
        self.chi2x = chi2x
        self.chi2y = chi2y
        self.chi2z = chi2z

        self.cos_tilt1 = cos_tilt1
        self.cos_tilt2 = cos_tilt2

        self.phi1 = phi1
        self.phi2 = phi2

        self.chi_eff = chi_eff

        self.z = z

        self.lambda1 = lambda1
        self.lambda2 = lambda2
        self.lambda_tilde = lambda_tilde

        self._convert_units()


    def _convert_units(self):
        # Pre-compute q+1 if q is already given
        if self.q is not None:
            self.q_plus_1 = self.q + 1.0

        # Compute total mass in source-frame.
        if self.M_source is None:
            # Obtain from component masses
            if (self.m1_source is not None) and (self.m2_source is not None):
                self.M_source = self.m1_source + self.m2_source
            # Obtain from chirp mass and symmetric mass ratio.
            elif (self.Mc_source is not None) and (self.eta is not None):
                self.M_source = self.eta**-(3.0/5.0) * self.Mc_source

        # Compute total mass in detector-frame.
        if self.M_det is None:
            # Obtain from component masses
            if (self.m1_det is not None) and (self.m2_det is not None):
                self.M_det = self.m1_det + self.m2_det
            # Obtain from chirp mass and symmetric mass ratio.
            elif (self.Mc_det is not None) and (self.eta is not None):
                self.M_det = self.eta**-(3.0/5.0) * self.Mc_det

        # Compute component masses in source-frame.
        if (self.m1_source is None) and (self.m2_source is None):
            # Obtain from total mass and mass ratio
            if (self.M_source is not None) and (self.q is not None):
                self.m1_source = self.M_source / self.q_plus_1
                self.m2_source = self.M_source - self.m1_source
            # Obtain from chirp mass and symmetric mass ratio.
            elif (self.Mc_source is not None) and (self.eta is not None):
                self.m1_source, self.m2_source = mc_eta_2_m1_m2(
                    self.Mc_source, self.eta
                )

        # Compute component masses in detector-frame.
        if (self.m1_det is None) and (self.m2_det is None):
            # Obtain from total mass and mass ratio
            if (self.M_det is not None) and (self.q is not None):
                self.m1_det = self.M_det / self.q_plus_1
                self.m2_det = self.M_det - self.m1_det
            # Obtain from chirp mass and symmetric mass ratio.
            elif (self.Mc_det is not None) and (self.eta is not None):
                self.m1_det, self.m2_det = mc_eta_2_m1_m2(
                    self.Mc_det, self.eta
                )

        # Obtain mass ratio from other coordinates.
        if self.q is None:
            # From source-frame component masses
            if (self.m1_source is not None) and (self.m2_source is not None):
                self.q = self.m2_source / self.m1_source
            # From detector-frame component masses
            elif (self.m1_det is not None) and (self.m2_det is not None):
                self.q = self.m2_det / self.m1_det

            if self.q is not None:
                # q+1 is sometimes convenient, so pre-compute
                self.q_plus_1 = self.q + 1.0

        # Obtain chirp mass and eta from other coordinates
        if self.eta is None:
            if (self.m1_det is not None) and (self.m2_det is not None):
                self.eta = (
                    self.m1_det*self.m2_det /
                    (self.M_det*self.M_det)
                )
            elif (self.m1_source is not None) and (self.m2_source is not None):
                self.eta = (
                    self.m1_source*self.m2_source /
                    (self.M_source*self.M_source)
                )

        if self.Mc_det is None:
            if (self.eta is not None) and (self.M_det is not None):
                self.Mc_det = self.eta**(3.0/5.0) * self.M_det

        if self.Mc_source is None:
            if (self.eta is not None) and (self.M_source is not None):
                self.Mc_source = self.eta**3.5 * self.M_source

        if self.z is not None:
            self.z_plus_1 = self.z + 1.0

            if (self.m1_source is None) and (self.m1_det is not None):
                self.m1_source = self.m1_det / self.z_plus_1
            elif (self.m1_source is not None) and (self.m1_det is None):
                self.m1_det = self.m1_source * self.z_plus_1

            if (self.m2_source is None) and (self.m2_det is not None):
                self.m2_source = self.m2_det / self.z_plus_1
            elif (self.m2_source is not None) and (self.m2_det is None):
                self.m2_det = self.m2_source * self.z_plus_1

            if (self.M_source is None) and (self.M_det is not None):
                self.M_source = self.M_det / self.z_plus_1
            elif (self.M_source is not None) and (self.M_det is None):
                self.M_det = self.M_source * self.z_plus_1

            if (self.Mc_source is None) and (self.Mc_det is not None):
                self.Mc_source = self.Mc_det / self.z_plus_1
            elif (self.Mc_source is not None) and (self.Mc_det is None):
                self.Mc_det = self.Mc_source * self.z_plus_1

    def copy(self):
        from copy import deepcopy
        return deepcopy(self)



parameter_priors = {
    "Mc_source" : 0.4,
    "Mc_det" : 0.4,
    "eta" : 4.0,
    "chi_eff" : 1.0,
    "chi1z" : 1.0,
    "chi2z" : 1.0,
    "lambda1" : 1000.0,
    "lambda2" : 1000.0,
    "lambda_tilde" : 1000.0,
}


parameter_npoints = {
    "Mc_det" : 15,
    "eta" : 15,
    "chi1z" : 15,
    "chi2z" : 15,
    "lambda1" : 20,
    "lambda2" : 20,
}


parameter_limits = {
    "Mc_det" : (0.0, numpy.inf),
    "eta" : (0.0, 0.25),
    "chi1z" : (-1.0, +1.0),
    "chi2z" : (-1.0, +1.0),
    "lambda1" : (0.0, numpy.inf),
    "lambda2" : (0.0, numpy.inf),
}


def valid_binary(parameters):
    if (parameters.m1_det is not None) and (parameters.m1_det <= 0.0):
        return False
    if (parameters.m2_det is not None) and (parameters.m2_det <= 0.0):
        return False
    if (parameters.m1_det is not None) and (parameters.m2_det is not None):
        if parameters.m2_det > parameters.m1_det:
            return False

    if (parameters.M_det is not None) and (parameters.M_det <= 0.0):
        return False
    if (parameters.q is not None) and not (0.0 < parameters.q <= 1.0):
        return False

    if (parameters.Mc_det is not None) and (parameters.Mc_det <= 0.0):
        return False
    if (parameters.eta is not None) and not (0.0 < parameters.eta <= 0.25):
        return False

    if (parameters.chi1z is not None) and (abs(parameters.chi1z) > 1.0):
        return False
    if (parameters.chi2z is not None) and (abs(parameters.chi2z) > 1.0):
        return False

    if (parameters.lambda1 is not None) and (parameters.lambda1 < 0.0):
        return False
    if (parameters.lambda2 is not None) and (parameters.lambda2 < 0.0):
        return False

    return True

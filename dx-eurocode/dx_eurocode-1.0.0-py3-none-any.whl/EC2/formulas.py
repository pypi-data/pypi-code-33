"""Recurrent formulas in EC2."""


def k62a(d):
    """Evaluate k in Eq. (6.2a)

    :param float d: The effective depth of a section of concrete ``[m]``
    :rtype: float
    """
    return 1 + (0.2/d)**0.5


def nu66N(fck):
    """Evaluate nu from Eq. (6.6N).

    :param fck: The characteristic strength of the concrete in MPa.
    :type fcd: float or int
    :rtype: float
    """
    return  0.6 * (1 - fck/250)


#: k factor in Eq. (6.47). See signature of `k62a`.
k647 = k62a

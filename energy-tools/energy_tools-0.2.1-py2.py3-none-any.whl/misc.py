from math import pi
from energy_tools.complex import EleComplex


def serie(z):
    """Puts impedances in serie (yep, simple summation).

    Args:
        z: List of impedances (either complex or real or a combination of both).

    Returns:
        Serie impedance.
    """
    return sum(z)


def parallel(z):
    """Puts impedances in parallel.

    Args:
        z: List of impedances (either complex or real or a combination of both).

    Returns:
        Parallel impedance.
    """
    try:
        return 1 / sum([1.0 / y for y in z])

    except ZeroDivisionError:
        return 0.0


def zCap(C, f=60):
    """Retourne l'impédance complexe d'un banc de condensateurs en fonction de
    la capacitance et de la fréquence (à 60Hz par défaut).
    """
    return EleComplex(1 / (2j * pi * f * C))


def zInd(L, f=60):
    """Retourne l'impédance complexe d'une inductance en fonction de
    l'inductance et de la fréquence (à 60Hz par défaut).
    """
    return EleComplex(2j * pi * f * L)

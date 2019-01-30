from math import atan, pi


class EleComplex(complex):
    """Improvement of the builtin complex type.

    Additional attributes:
        phase: Returns the complex number's phase in degrees.
        module: Returns the complex number's unitless amplitude.
    """

    @property
    def phase(self):
        """Returns the complex number's phase in degrees.
        """
        if self.real > 0:
            if self.imag >= 0:
                return abs(180 * atan(self.imag / self.real) / pi)
            else:
                return 360 - abs(180 * atan(self.imag / self.real) / pi)
        elif self.real < 0:
            if self.imag >= 0:
                return 180 - abs(180 * atan(self.imag / self.real) / pi)
            else:
                return 180 + abs(180 * atan(self.imag / self.real) / pi)
        else:
            if self.imag == 0:
                return 0.0
            elif self.imag > 0:
                return 90.0
            else:
                return 270.0

    @property
    def module(self):
        return abs(self)

    def __round__(self, ndigits=None):
        return EleComplex(round(self.real, ndigits) + round(self.imag, ndigits)*1j)


def complex_impedance(z, xr):
    """Returns a complex impedance based on an impedance *z* and the X/R ratio.

    Args:
        z: Unitless impedance value.
        xr: X/R ratio.

    Returns:
        Complex impedance (EleComplex).
    """

    z = float(abs(z))
    xr = float(abs(xr))
    real = (z ** 2 / (1 + xr ** 2)) ** 0.5
    try:
        imag = (z ** 2 / (1 + 1 / xr ** 2)) ** 0.5
    except ZeroDivisionError:
        imag = 0.0
    return EleComplex(real, imag)

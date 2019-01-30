from math import cos, pi, sin, sqrt
from numpy import matrix

from energy_tools.complex import EleComplex


class Phasor(object):
    """New data type for the electrical phasor used in power engineering.

    A phasor is defined by an amplitude and a phase. The instance can be created either
    using those, or by providing a complex amplitude (in this case the phase is
    ignored). Several operations are supported, including: addition, substraction,
    multiplication, division, power, inversion and equality with either another phasor,
    a float or an integer.

    It also provides a nice representation in this form:

        120.000 @ 0.000°

    Attributes:
        amp: The unitless phasor amplitude.
        pha: The phasor's phase in degrees.
        real: The phasor's real part (interpreted as a complex number).
        imag: The phasor's imaginary part (interpreted as a complex number).
    """

    def __init__(self, amp, pha=0.0):
        """Initialize the phasor either using a real amplitude and a phase, or a
        complex amplitude.

        Args:
            amp: The unitless phasor amplitude.
            pha: The phasor's phase in degrees.
        """

        if amp.__class__ == complex:
            new_complex = EleComplex(amp)
            self.amp = new_complex.module
            self.pha = new_complex.phase

        elif amp.__class__ == EleComplex:
            self.amp = amp.module
            self.pha = amp.phase

        else:
            if amp.__class__ == int:
                amp = float(amp)

            if pha.__class__ == int:
                pha = float(pha)

            if amp >= 0:
                self.amp = amp
            elif amp < 0:
                self.amp = -amp
                pha += 180

            if pha < 0:
                self.pha = pha % -360 + 360
            else:
                self.pha = pha % 360

    @property
    def real(self):
        return self.amp * cos(self.pha * pi / 180)

    @property
    def imag(self):
        return self.amp * sin(self.pha * pi / 180)

    def __add__(self, other):
        if other.__class__ == int or other.__class__ == float:
            return self.__add__(Phasor(other, 0))

        elif other.__class__ == EleComplex:
            return self.__add__(Phasor(other))

        elif other.__class__ == Phasor:
            x1 = self.amp * cos(self.pha * pi / 180)
            y1 = self.amp * sin(self.pha * pi / 180)
            x2 = other.amp * cos(other.pha * pi / 180)
            y2 = other.amp * sin(other.pha * pi / 180)
            a = sqrt(pow(x1 + x2, 2) + pow(y1 + y2, 2))
            p = EleComplex(x1 + x2 + (y1 + y2) * 1j).phase
            return Phasor(a, p)

        else:
            return NotImplemented

    def __sub__(self, other):
        if other.__class__ == int or other.__class__ == float:
            return self.__sub__(Phasor(other, 0))

        elif other.__class__ == complex:
            return self.__sub__(Phasor(other))

        elif other.__class__ == Phasor:
            x1 = self.amp * cos(self.pha * pi / 180)
            y1 = self.amp * sin(self.pha * pi / 180)
            x2 = other.amp * cos(other.pha * pi / 180)
            y2 = other.amp * sin(other.pha * pi / 180)
            a = sqrt(pow(x1 - x2, 2) + pow(y1 - y2, 2))
            p = EleComplex(x1 - x2 + (y1 - y2) * 1j).phase
            return Phasor(a, p)

        else:
            return NotImplemented

    def __mul__(self, other):
        if other.__class__ == int or other.__class__ == float:
            return self.__mul__(Phasor(other, 0))

        elif other.__class__ == EleComplex:
            return self.__mul__(Phasor(other))

        elif other.__class__ == Phasor:
            return Phasor(self.amp * other.amp, self.pha + other.pha)

        else:
            return NotImplemented

    def __truediv__(self, other):
        if other.__class__ == int or other.__class__ == float:
            return self.__truediv__(Phasor(other, 0))

        elif other.__class__ == EleComplex:
            return self.__truediv__(Phasor(other))

        elif other.__class__ == Phasor:
            return Phasor(self.amp / other.amp, self.pha - other.pha)

        else:
            return NotImplemented

    def __radd__(self, other):
        if other.__class__ == int or other.__class__ == float:
            return self.__add__(Phasor(other, 0))

        elif other.__class__ == EleComplex:
            return self.__add__(Phasor(other))

        else:
            return NotImplemented

    def __rsub__(self, other):
        if other.__class__ == int or other.__class__ == float:
            x1 = self.amp * cos((self.pha + 180) * pi / 180)
            y1 = self.amp * sin((self.pha + 180) * pi / 180)
            x2 = other
            y2 = 0
            a = sqrt(pow(x1 + x2, 2) + pow(y1 + y2, 2))
            p = EleComplex(x1 + x2 + (y1 + y2) * 1j).phase
            return Phasor(a, p)

        else:
            return NotImplemented

    def __rmul__(self, other):
        if other.__class__ == int or other.__class__ == float:
            return self.__mul__(Phasor(other, 0))

        elif other.__class__ == EleComplex:
            return self.__mul__(Phasor(other))

        else:
            return NotImplemented

    def __rtruediv__(self, other):
        if other.__class__ == int or other.__class__ == float:
            a = other / self.amp
            if self.pha >= 180:
                p = self.pha - 180
            else:
                p = self.pha + 180
            return Phasor(a, p)

        else:
            return NotImplemented

    def __pow__(self, other, modulo=None):
        if modulo is not None:
            return NotImplemented

        elif other.__class__ == int:
            r = 1
            for i in range(other):
                r = self * r
            return r

        else:
            return NotImplemented

    def __abs__(self):
        return self.amp

    def __neg__(self):
        return self.__rsub__(0)

    def __pos__(self):
        return self

    def __invert__(self):
        return self.__neg__()

    def __int__(self):
        return int(self.amp)

    def __float__(self):
        return float(self.amp)

    def __complex__(self):
        return EleComplex(self.real, self.imag)

    def __round__(self, n=0):
        return Phasor(round(self.amp, n), round(self.pha, n))

    def __repr__(self):
        s = str(round(self.amp, 3)) + " @ "
        s += str(round(self.pha, 3)) + "°"
        return s

    def __eq__(self, other):
        if other.__class__ == int or other.__class__ == float:
            other = Phasor(other, 0)
        elif other.__class__ != Phasor:
            return False
        elif round(self.amp, 2) != round(other.amp, 2):
            return False
        elif round(self.pha, 1) != round(other.pha, 1):
            return False
        else:
            return True

    def __ne__(self, other):
        return not self.__eq__(other)


def sequences(v_a, v_b, v_c):
    """Returns phase A's sequence voltages from phases A, B and C's voltages.

    Args:
        v_a: Phase A voltage.
        v_b: Phase B voltage.
        v_c: Phase C voltage.

    Returns:
        v_a0, v_a1, v_a2: Zero, positive and negative sequence voltages for phase A.
    """
    a = Phasor(1, 120)
    At = matrix(
        [[1 / 3, 1 / 3, 1 / 3], [1 / 3, a / 3, a ** 2 / 3], [1 / 3, a ** 2 / 3, a / 3]]
    )
    Vabc = matrix([[Va], [Vb], [Vc]])
    Va012 = At * Vabc
    return Va012[0].item(), Va012[1].item(), Va012[2].item()


def phasors(v_a0, v_a1, v_a2):
    """Returns phase A, B and C's voltages from phases A's sequence voltages.

    Args:
        v_a0: Zero sequence voltages for phase A.
        v_a1: Positive sequence voltages for phase A.
        v_a2: Negative sequence voltages for phase A.

    Returns:
        v_a, v_b, v_c: Phases A, B and C's voltages.
    """
    a = Phasor(1, 120)
    A = matrix([[1, 1, 1], [1, a ** 2, a], [1, a, a ** 2]])
    Va012 = matrix([[v_a0], [v_a1], [v_a2]])
    Vabc = A * Va012
    return Vabc[0].item(), Vabc[1].item(), Vabc[2].item()

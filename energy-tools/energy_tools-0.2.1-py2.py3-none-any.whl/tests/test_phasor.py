from energy_tools.complex import EleComplex
from energy_tools.phasor import Phasor


# TODO(miek770): Add tests for sequences() and phasors().


def test_phasor_addition():
    v1 = Phasor(7.0, 0.0)
    v2 = Phasor(4.0, 45.0)
    v3 = Phasor(10.23, 16.05)
    ans = v1 + v2
    assert ans == v3


def test_phasor_addition_triple():
    v1 = Phasor(10, 20)
    v2 = Phasor(15, 90)
    v3 = Phasor(7, 190)
    v4 = Phasor(17.39, 81.72)
    assert sum((v1, v2, v3)) == v4


def test_phasor_soustraction():
    v1 = Phasor(1.5, 90)
    v2 = Phasor(2.6, 145)
    v3 = Phasor(2.13, 0.24)
    ans = v1 - v2
    print(ans)
    print(v3)
    assert ans == v3


def test_phasor_soustraction_et_addition():
    v1 = Phasor(22, 140)
    v2 = Phasor(40, 190)
    v3 = Phasor(15, 290)
    v4 = Phasor(28.54, 14.18)
    assert v1 - v2 + v3 == v4


def test_phasor_egalite():
    assert Phasor(7.0, 0.0) == Phasor(7.0, 0.0)


def test_phasor_multiplication():
    v1 = Phasor(6, 30)
    v2 = Phasor(8, -45)
    v3 = Phasor(48, -15)
    assert v1 * v2 == v3


def test_phasor_division():
    v1 = Phasor(6, 30)
    v2 = Phasor(8, -45)
    v3 = Phasor(0.75, 75)
    assert v1 / v2 == v3


def test_phasor_puissance_cube():
    v1 = Phasor(2, 10)
    v2 = Phasor(8, 30)
    assert pow(v1, 3) == v2


def test_phasor_puissance_carre():
    v1 = Phasor(20, 270)
    v2 = Phasor(400, 180)
    assert pow(v1, 2) == v2


def test_phasor_puissance_carre_2():
    v1 = Phasor(20, 270)
    v2 = Phasor(400, 180)
    assert v1 ** 2 == v2


def test_phasor_representation_decimal():
    v1 = Phasor(2.14, 127.12)
    assert v1.__repr__() == "2.14 @ 127.12°"


def test_phasor_representation_entier():
    v1 = Phasor(2, 127)
    assert v1.__repr__() == "2.0 @ 127.0°"


def test_phasor_complexe():
    v1 = Phasor(3.0 + 4.0j)
    assert v1.__repr__() == "5.0 @ 53.13°"


def test_phasor_complexe_real():
    v1 = Phasor(3.0 + 4.0j)
    assert v1.real == 3.0


def test_phasor_complexe_imag():
    v1 = Phasor(3.0 + 4.0j)
    assert v1.imag == 4.0


def test_phasor_multiplication_complexe():
    v1 = Phasor(3.0 + 4.0j)
    assert EleComplex(3.0 + 4.0j) * v1 == pow(v1, 2)

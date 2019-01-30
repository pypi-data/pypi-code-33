from math import sqrt

from energy_tools.complex import EleComplex


def test_init():
    assert EleComplex(1, 2) == complex(1, 2)


def test_phase_simple():
    assert EleComplex(1, 1).phase == 45


def test_phase_quadran_1():
    assert EleComplex(1 + 1j).phase == 45.0


def test_phase_quadran_2():
    assert EleComplex(-1 + 1j).phase == 135.0


def test_phase_quadran_3():
    assert EleComplex(-1 - 1j).phase == 225.0


def test_phase_quadran_4():
    assert EleComplex(1 - 1j).phase == 315.0


def test_phase_0_degres():
    assert EleComplex(1 + 0j).phase == 0.0


def test_phase_90_degres():
    assert EleComplex(0 + 1j).phase == 90.0


def test_phase_180_degres():
    assert EleComplex(-1 + 0j).phase == 180.0


def test_phase_270_degres():
    assert EleComplex(0 - 1j).phase == 270.0


def test_phase_entier_positif():
    assert EleComplex(2).phase == 0.0


def test_phase_decimal_negatif():
    assert EleComplex(-2.12).phase == 180.0


def test_module():
    assert EleComplex(1, 1).module == sqrt(2)


def test_round_2_digits():
    assert round(EleComplex(1.1032 + 1.1240j), 2) == EleComplex(1.10 + 1.12j)


def test_round():
    assert round(EleComplex(1.1032 + 1.1240j)) == EleComplex(1.0 + 1.0j)


def test_round_str():
    assert round(EleComplex(1.1032 + 1.1240j), 3).__str__() == "(1.103+1.124j)"

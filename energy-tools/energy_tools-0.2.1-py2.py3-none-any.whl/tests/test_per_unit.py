from pytest import approx
from energy_tools.per_unit import *


def test_i_base_ka():
    assert i_base_ka(100, 120) == approx(0.481125)


def test_z_base_ohm_ib():
    assert z_base_ohm(120, ib_ka=0.481125) == approx(144)


def test_z_base_ohm_sb():
    assert z_base_ohm(120, sb_mva=100) == approx(144)


def test_s_base_mva():
    assert s_base_mva(120, 0.481125) == approx(100)

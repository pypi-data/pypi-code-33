from pytest import approx
from energy_tools.energy_factors import *


def test_facteur_utilisation():
    P = 4.2  # MW
    heures = [571, 1264, 713, 730, 344, 341, 565, 329, 315, 315, 1431, 1847]
    mw = [
        0.000,
        0.210,
        0.630,
        1.050,
        1.470,
        1.890,
        2.310,
        2.730,
        3.150,
        3.570,
        3.990,
        4.200,
    ]
    ans = utilisation_factor(heures, mw, P)
    assert ans == approx(0.554592)


def test_facteur_de_pertes():
    P = 4.2  # MW
    heures = [571, 1264, 713, 730, 344, 341, 565, 329, 315, 315, 1431, 1847]
    mw = [
        0.000,
        0.210,
        0.630,
        1.050,
        1.470,
        1.890,
        2.310,
        2.730,
        3.150,
        3.570,
        3.990,
        4.200,
    ]
    ans = loss_factor(heures, mw, P)
    assert ans == approx(0.459638)


# def test_calc_mwh():
# from energy_tools.prod_vent import calc_mwh

# heures = [571, 1264, 713, 730, 344, 341, 565, 329, 315, 315, 1431, 1847]
# mw = [
# 0.000,
# 0.210,
# 0.630,
# 1.050,
# 1.470,
# 1.890,
# 2.310,
# 2.730,
# 3.150,
# 3.570,
# 3.990,
# 4.200,
# ]
# ans = calc_mwh(heures, mw)
# mwh = [0.00, 0.27, 0.45, 0.77, 0.51, 0.64, 1.31, 0.90, 0.99, 1.12, 5.71, 7.76]
# assert ans == mwh

from pytest import approx, raises
from energy_tools.misc import parallel, serie


def test_serie_resistances():
    assert serie((2, 3.5)) == 5.5


def test_serie_impedances():
    assert approx(serie((2 + 1j, 3.0 - 2.8j))) == 5 - 1.8j


def test_serie_erreur_type():
    with raises(TypeError):
        serie("test")


def test_parallel_resistances():
    assert parallel((2.4, 1.2)) == 0.8


def test_parallel_impedances():
    ans = parallel((310.2 + 12.4j, 18.3 - 132.7j))
    assert ans.real + ans.imag * 1j == approx(59.893270 - 102.683286j)

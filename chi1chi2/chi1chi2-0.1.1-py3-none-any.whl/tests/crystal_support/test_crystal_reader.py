import os
import unittest

from chi1chi2.crystal_support.crystal_reader import read_optimized_coords, read_coords_charges
from chi1chi2.utils.constants import Params, PI2, PI, simeq
from chi1chi2.utils.molecule_reader_writer import from_file


def file_for_test(file):
    return os.path.join(os.path.dirname(__file__), file)


FRA_REFERENCE = file_for_test("mil_ga.fra")
FRC_REFERENCE = file_for_test("mil_ga_chg.fra")
OPT_OUTPUT = file_for_test("mil_ga.out")
SCFLOG_OUTPUT = file_for_test("mil_ga.SCFLOG")

PARAMETERS_PARAMETER_READER = [["5.2", Params.orthogonal(5.2, 5.2, 5.2)],
                               ["7 8", Params(7., 7., 8., PI2, PI2, PI2 * 4 / 3)],
                               ["5. 8. 10.", Params.orthogonal(5., 8., 10.)],
                               ["5. 7. 10. 95.", Params.monoclinic(5., 7., 10., 95. / 180. * PI)],
                               ["5 7. 10. 91. 92. 93.", Params(5., 7., 10., *[u * PI / 180. for u in (91, 92, 93)])]]


class TestGeomReader(unittest.TestCase):
    def test_param_reader(self):
        for inp, exptd_params in PARAMETERS_PARAMETER_READER:
            with self.subTest(msg=inp):
                params = Params.from_line(inp)
                self.assertEqual(exptd_params, params)

    def test_param_reader_tetragonal(self):
        inp = "5. 7. 10."
        exptd_params = Params(5, 7, 10, PI2, PI2, PI2)

        self.assertEqual(exptd_params, Params.from_line(inp, True))

    def test_volume_from_params(self):
        params = Params.from_line("1 2 3")
        params2 = Params.from_line("1 2 3 30")

        self.assertEqual(6., params.volume())
        self.assertTrue(simeq(3., params2.volume()))

    def test_reader(self):
        fra_reference = from_file(FRA_REFERENCE)

        fra_molecule = read_optimized_coords(OPT_OUTPUT)

        self.assertEqual(fra_reference, fra_molecule)

    def test_reader_charges(self):
        fra_reference = from_file(FRC_REFERENCE)

        fra_molecule = read_coords_charges(OPT_OUTPUT, SCFLOG_OUTPUT)

        self.assertEqual(fra_reference, fra_molecule)

import os
from unittest import TestCase

from chi1chi2.input.input_preparator import Input
from chi1chi2.utils.constants import ChiException, simeq
from chi1chi2.utils.molecule_reader_writer import from_file
from tests.molecule.test_molecule import lists_almost_equal

MNA_INPUT = "mna_input.inp"
MNAS_INPUT = "mna_input2.inp"
MNA_WRONG_INPUT = "mna_input_broken.inp"

MNA_CHG = "mna_chg.dat"
MNA_CHG1 = "mna_chg1.dat"
MNA_CHG2 = "mna_chg2.dat"


def file_for_test(file):
    return os.path.join(os.path.dirname(__file__), file)


test_parameters = [["standard one-molecule only", "mna_input.inp", "mna_uc.fra", "mna_uc.xyz"],
                   ["one-molecule one skip", "mna_input_skp1.inp", "mna_uc_skp1.fra", "mna_uc_skp1.xyz"],
                   ["two-molecule, one skip", "mna_input_skp2.inp", "mna_uc_skp1.fra", "mna_uc_skp1.xyz"]]


def assert_numeric_almost_equal(exptd_list, actual_list, message=''):
    for i in range(len(exptd_list)):
        exptd_tokens = exptd_list[i].split()
        actual_tokens = actual_list[i].split()
        for j in range(len(exptd_tokens)):
            if not simeq(float(exptd_tokens[j]), float(actual_tokens[j])):
                raise AssertionError(message)


class TestInputGenerator(TestCase):
    def test_should_reproduce_unit_cell(self):
        for description, input_file, exptd_fra_file, exptd_xyz_file in test_parameters:
            with self.subTest(msg="checking: ", setup=description):
                supermolecule_fra_exptd = from_file(file_for_test(exptd_fra_file))
                supermolecule_xyz_exptd = from_file(file_for_test(exptd_xyz_file))

                input = Input.from_file(file_for_test(input_file))
                supermolecule_fra = input.get_fra_supermolecule(input.flags)
                supermolecule_xyz = supermolecule_fra.to_xyz_molecule()

                failures = ""
                if supermolecule_fra_exptd != supermolecule_fra:
                    failures += "fra file check failed for subtest: " + description + "; "
                if supermolecule_xyz_exptd != supermolecule_xyz:
                    failures += "xyz file check failed for subtest: " + description
                if len(failures) != 0:
                    self.fail(failures)

    def test_lorentz(self):
        input = Input.from_file(file_for_test(MNA_INPUT))
        with open(file_for_test("mna_lorentz.dat")) as f:
            expected_mna_lorentz_input = [line.strip() for line in f.readlines()]

        mna_lorentz_input = input.for_lorentz().split('\n')

        assert_numeric_almost_equal(expected_mna_lorentz_input, mna_lorentz_input,
                                    "difference in generated input for Lorentz calculations - mna")

    def test_lorentz_2_molecules_in_uc(self):
        input = Input.from_file(file_for_test(MNAS_INPUT))
        with open(file_for_test("mna_lorentz.dat")) as f:
            expected_mna_lorentz_input = [line.strip() for line in f.readlines()]
        groups_expected = [[float(u) for u in l.split()[:3]] for l in expected_mna_lorentz_input[3:-1]]

        mna_lorentz_input = input.for_lorentz().split('\n')
        groups = [[float(u) for u in l.split()[:3]] for l in mna_lorentz_input[3:-1]]

        assert_numeric_almost_equal(expected_mna_lorentz_input[:3], mna_lorentz_input[:3],
                                    "difference in generated input for Lorentz calculations - mnas (header)")
        if not lists_almost_equal(groups_expected, groups):
            self.fail("difference in generated input for Lorentz calculations - mnas (groups)")

    def test_should_fail_when_wronng_first_symmetry_operation_in_input_file(self):
        with self.assertRaises(ChiException):
            Input.from_file(file_for_test(MNA_WRONG_INPUT))

    def test_input_for_charge_generation_single_molecule(self):
        with open(file_for_test(MNA_CHG)) as f:
            ref_chg_lines = f.readlines()

        input = Input.from_file(file_for_test(MNA_INPUT))
        chg_lines = input.for_charge_generation()[0].split('\n')

        assert_numeric_almost_equal(ref_chg_lines, chg_lines, "single molecule charge input generation problem")

    def test_inputs_for_charge_generation_two_molecules(self):
        with open(file_for_test(MNA_CHG1)) as f:
            ref_chg_lines1 = f.readlines()
        with open(file_for_test(MNA_CHG2)) as f:
            ref_chg_lines2 = f.readlines()

        input = Input.from_file(file_for_test(MNAS_INPUT))
        chg_lines = [lines.split('\n') for lines in input.for_charge_generation()]

        assert_numeric_almost_equal(ref_chg_lines1, chg_lines[0], "two molecule charge input generation problem, mol 1")
        assert_numeric_almost_equal(ref_chg_lines2, chg_lines[1], "two molecule charge input generation problem, mol 2")

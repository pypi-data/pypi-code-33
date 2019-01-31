import os
import unittest

from chi1chi2.cif.cif_parser import Cif, escape_atomic_symbol, escape_stdev
from chi1chi2.input.input_preparator import Input
from chi1chi2.utils.constants import Params, Symmop
from chi1chi2.utils.molecule_reader_writer import from_file


def file_for_test(file):
    return os.path.join(os.path.dirname(__file__), file)


COANP_CIF = file_for_test("coanp.cif")
COANP_FRA = file_for_test("coanp.fra")
MNA_CIF = file_for_test("mna.cif")
MNA_INPUT = file_for_test("mna_input.inp")
MNA_INPUT_FROM_CIF = file_for_test("mna_input_cif.inp")

strings_for_escaping_test = [["1.2(3)", "1.2"],
                             ["-2.42343(12)", "-2.42343"],
                             ["1.32(5)", "1.32"],
                             ["90", "90"]]

strings_for_escaping_labels_test = [["H7A", "H"],
                                    ["C5A", "C"],
                                    ["H5A", "H"],
                                    ["C6A", "C"],
                                    ["N8", "N"],
                                    ["C2A", "C"],
                                    ["H2A", "H"]]

expected_atoms = []

cif = Cif.from_file(COANP_CIF)
ref_mol = from_file(COANP_FRA)


class TestCifParser(unittest.TestCase):
    def test_get_symmops(self):
        exptd_symmops = [Symmop.from_line(line) for line in ['x,y,z', '-x,-y,1/2+z', '1/2+x,-y,z', '1/2-x,y,1/2+z']]

        self.assertListEqual(exptd_symmops, cif.get_symmops())

    def test_escape_sequence(self):
        for inp, expected_result in strings_for_escaping_test:
            with self.subTest(msg=inp + " -> " + expected_result):
                self.assertEqual(expected_result, escape_stdev(inp))

    def test_escape_atom_label(self):
        for inp, exptd_result in strings_for_escaping_labels_test:
            self.assertEqual(exptd_result, escape_atomic_symbol(inp))

    def test_get_params(self):
        exptd_params = Params.orthogonal(26.099, 6.637, 7.555)

        self.assertEqual(exptd_params, cif.get_params())
        self.assertEqual(ref_mol.params, cif.get_params())

    def test_get_atoms(self):
        exptd_atoms = ref_mol.atoms

        self.assertEqual(exptd_atoms, cif.get_atoms())

    def test_should_provide_input_stub_from_cif_file(self):
        exptd_input = Input.from_file(MNA_INPUT_FROM_CIF)

        cif = Cif.from_file(MNA_CIF)
        actual_input = cif.get_input()
        exptd_groups = [[1, 1, 2, 1, 2, 2, 4, 3, 1, 1, 1]]

        self.assertTupleEqual(exptd_input.params, actual_input.params)
        self.assertEqual(exptd_input.fra_molecules, actual_input.fra_molecules)
        self.assertEqual(exptd_input.symmops, actual_input.symmops)
        self.assertEqual(exptd_input.flags, actual_input.flags)
        self.assertEqual(exptd_input.asym_groups, exptd_groups)

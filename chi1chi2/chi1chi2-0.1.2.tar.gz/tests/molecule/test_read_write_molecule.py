import os
import unittest

from chi1chi2.utils.constants import Params
from chi1chi2.utils.molecule_reader_writer import from_file, write_mol_to_file


def file_for_test(file):
    return os.path.join(os.path.dirname(__file__), file)


SAMPLE_SHUFFLED_MOLECULE = file_for_test('mna_shuf.xyz')
SAMPLE_REORDERED_MOLECULE = file_for_test('mna_shuf_reordered.xyz')
TEMP_XYZ_FILE = file_for_test('test.xyz')
TEMP_FRA_FILE = file_for_test('test.fra')
SAMPLE_FRA_FILE = file_for_test('mna.fra')
SAMPLE_XYZ_FILE = file_for_test('mna.xyz')
SAMPLE_CHG_XYZ_FILE = file_for_test('mna_chg.xyz')


class TestRWMolecule(unittest.TestCase):
    def setUp(self):
        self.clean_temp_mol_file_if_present()

    def tearDown(self):
        self.clean_temp_mol_file_if_present()

    def clean_temp_mol_file_if_present(self):
        for f in (TEMP_FRA_FILE, TEMP_XYZ_FILE):
            if os.path.isfile(f):
                os.remove(f)

    def test_read_from_file(self):
        mol = from_file(SAMPLE_SHUFFLED_MOLECULE)

        self.assertTupleEqual(mol.params, Params.default())
        self.assertEqual(len(str(mol).split('\n')), (19 + 3))

    def test_write_to_file(self):
        mol = from_file(SAMPLE_SHUFFLED_MOLECULE)

        write_mol_to_file(mol, TEMP_XYZ_FILE)
        mol2 = from_file(TEMP_XYZ_FILE)

        self.assertTrue(os.path.isfile(TEMP_XYZ_FILE))
        self.assertEqual(mol, mol2)

    def test_read_from_frac_file(self):
        mol_ref = from_file(SAMPLE_XYZ_FILE)

        mol = from_file(SAMPLE_FRA_FILE)
        mol = mol.to_xyz_molecule()

        self.assertEqual(mol, mol_ref)

    def test_write_frac_file(self):
        mol_ref = from_file(SAMPLE_XYZ_FILE)
        mol_to_write = mol_ref.to_fra_molecule()

        write_mol_to_file(mol_to_write, TEMP_FRA_FILE)
        mol = from_file(TEMP_FRA_FILE)
        mol = mol.to_xyz_molecule()

        self.assertEqual(mol, mol_ref)

    def test_should_read_xyz_with_charges(self):
        mol_ref = from_file(SAMPLE_XYZ_FILE)

        mol = from_file(SAMPLE_CHG_XYZ_FILE)

        self.assertEqual(mol, mol_ref)

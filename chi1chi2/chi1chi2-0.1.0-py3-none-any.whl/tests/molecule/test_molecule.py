import numbers
import os
import unittest

import numpy as np

from chi1chi2.utils.constants import simeq, Params
from chi1chi2.utils.molecule import Atom, Unit, Molecule
from chi1chi2.utils.molecule_reader_writer import from_file
from chi1chi2.utils.molecule_reorderer import reorder, adjust_hydrogens, is_ordered, get_groups, \
    reorder_and_group_by_charge, group_by_charge, get_molecules_by_groups, get_molecule_with_generated_charges

PLACES = 5

ONE_BOHR_IN_A = Unit.Bohr.to_angstrom()


def file_for_test(file_name):
    return os.path.join(os.path.dirname(__file__), file_name)


SAMPLE_MOLECULE_ORDERED_BY_HAND = 'mna.xyz'
SAMPLE_MOLECULES_ORDERED_BY_HAND = 'mnas.xyz'
SAMPLE_MOLECULES_ORDERED_BY_HAND1 = 'mnas1.xyz'
SAMPLE_MOLECULES_ORDERED_BY_HAND2 = 'mnas2.xyz'
SAMPLE_SHUFFLED_MOLECULE = 'mna_shuf.xyz'
SAMPLE_REORDERED_MOLECULE = 'mna_shuf_reordered.xyz'
SAMPLE_SHUFFLED_MOLECULES = 'mnas_shuf.xyz'
SAMPLE_REORDERED_MOLECULES = 'mnas_shuf_reordered.xyz'
SAMPLE_CIF_MOLECULE = 'mna_cif.xyz'
SAMPLE_CIF_HYDROGEN_ADJUSTED_MOLECULE = 'mna_cif_adjusted.xyz'
MNAS_NA = "mnas_na.xyz"
MNAS_NA2 = "mnas_na2.xyz"
MNAS_NA3 = "mnas_na3.xyz"


def _compare_inner(lst1, lst2):
    if isinstance(lst1, numbers.Number) and isinstance(lst2, numbers.Number):
        if simeq(lst1, lst2):
            return True
        else:
            print("difference in: " + str(lst1) + " vs. " + str(lst2))
    else:
        return all([_compare_inner(lst1[i], lst2[i]) for i in range(len(lst1))])


def lists_almost_equal(exptd_lst, lst):
    if exptd_lst and lst:
        if len(exptd_lst) != len(lst):
            print("wrong lists dimensions: " + exptd_lst + " vs. " + lst)
            return False
        return all([_compare_inner(exptd_lst[i], lst[i]) for i in range(len(exptd_lst))])
    else:
        return True


class TestMolecule(unittest.TestCase):
    def test_atom_angstrom(self):
        line = "C 1. 2. 3."

        atom = Atom.from_line(line)

        self.assertTupleEqual(atom.get_coords(), (1., 2., 3.))

    def test_atom_bohr(self):
        atom = Atom("C", 1, 2, 3, unit=Unit.Bohr)

        coords = atom.get_coords()

        self.assertAlmostEqual(coords[0], ONE_BOHR_IN_A, PLACES)
        self.assertAlmostEqual(coords[1], 2 * ONE_BOHR_IN_A, PLACES)
        self.assertAlmostEqual(coords[2], 3 * ONE_BOHR_IN_A, PLACES)

    def test_should_reorder_shuffled(self):
        mol_shuffled = from_file(file_for_test(SAMPLE_SHUFFLED_MOLECULE))
        mol_ref = from_file(file_for_test(SAMPLE_REORDERED_MOLECULE))
        expected_groups = [[2, 1, 2, 1, 2, 1, 1, 1, 1, 3, 4]]

        mol_shuffled, groups = reorder(mol_shuffled)

        self.assertEqual(mol_ref, mol_shuffled)
        self.assertListEqual(groups, expected_groups)

    def test_should_reorder_two_shuffled(self):
        mols_shuffled = from_file(file_for_test(SAMPLE_SHUFFLED_MOLECULES))
        mols_ref = from_file(file_for_test(SAMPLE_REORDERED_MOLECULES))
        expected_groups = [[2, 1, 2, 1, 2, 1, 1, 1, 1, 3, 4], [2, 1, 2, 1, 2, 1, 1, 1, 1, 3, 4]]

        mols_shuffled, groups = reorder(mols_shuffled)

        self.assertEqual(mols_ref, mols_shuffled)
        self.assertListEqual(groups, expected_groups)

    def test_should_adjust_hydrogens_to_equib_length_based_on_covalent_radii(self):
        mol = from_file(file_for_test(SAMPLE_CIF_MOLECULE))
        mol_ref = from_file(file_for_test(SAMPLE_CIF_HYDROGEN_ADJUSTED_MOLECULE))

        mol = adjust_hydrogens(mol)

        self.assertEqual(mol_ref, mol)

    def test_should_produce_groups_one_molecule(self):
        mol = from_file(file_for_test(SAMPLE_REORDERED_MOLECULE))
        exptd_groups = [[]]
        with open(file_for_test("groups_mna_reordered")) as f:
            for line in f.readlines():
                exptd_groups[0].append([float(u) for u in line.split()[:3]])
        exptd_groups.append([11])

        groups = list(reorder_and_group_by_charge(mol))

        if not lists_almost_equal(exptd_groups, groups):
            self.fail("failed to produce groups for one molecule with ordering")

    def test_should_produce_groups_two_molecules(self):
        mol = from_file(file_for_test(SAMPLE_REORDERED_MOLECULES))
        exptd_groups = [[]]
        with open(file_for_test("groups_mnas_reordered")) as f:
            for line in f.readlines():
                exptd_groups[0].append([float(u) for u in line.split()[:3]])
        exptd_groups.append([11, 11])

        groups = list(reorder_and_group_by_charge(mol))

        if not lists_almost_equal(exptd_groups, groups):
            self.fail("failed to produce groups for two molecules with ordering")

    def test_should_produce_groups_for_molecule_ordered_by_hand(self):
        mol = from_file(file_for_test(SAMPLE_MOLECULES_ORDERED_BY_HAND))
        exptd_groups = [[]]
        with open(file_for_test("groups_mna")) as f:
            for line in f.readlines():
                exptd_groups[0].append([float(u) for u in line.split()[:3]])
        exptd_groups.append([11])

        groups = list(group_by_charge(mol, get_groups(mol)))

        if not lists_almost_equal(exptd_groups, groups):
            self.fail("failed to produce groups for one molecule ordered by hand")

    def test_cm_co(self):
        co = Molecule([Atom('C', 0, 0, 0),
                       Atom('O', 1.128, 0, 0)],
                      Params.default())
        cm_exptd = np.array([0.644571428571429, 0., 0.]).reshape((3, 1))

        co_cq = co.cq()

        if not lists_almost_equal(cm_exptd.tolist(), co_cq.tolist()):
            self.fail("error in determining the center of the nuclear charge for co!")

    def test_cm_h2o(self):
        h2o = Molecule([Atom('O', 0, 0, 0.119262),
                        Atom('H', 0, 0.763239, -0.477047),
                        Atom('H', 0, -0.763239, -0.477047)],
                       Params.default())
        cm_exptd = np.zeros((3, 1))

        h2o_cq = h2o.cq()

        if not lists_almost_equal(cm_exptd.tolist(), h2o_cq.tolist()):
            self.fail("error in determining the center of the nuclear charge for h2o!")

    def test_should_return_true_for_molecule_ordered_by_hand(self):
        mna = from_file(file_for_test(SAMPLE_MOLECULE_ORDERED_BY_HAND))
        expected_groups = [[1, 1, 2, 1, 2, 2, 4, 3, 1, 1, 1]]

        self.assertTrue(is_ordered(mna))

        groups = get_groups(mna)

        self.assertListEqual(expected_groups, groups)

    def test_should_return_groups_for_molecules_ordered_by_hand(self):
        mnas = from_file(file_for_test(SAMPLE_MOLECULES_ORDERED_BY_HAND))
        expected_groups = [[1, 1, 2, 1, 2, 2, 4, 3, 1, 1, 1], [1, 1, 2, 1, 2, 2, 4, 3, 1, 1, 1]]

        self.assertTrue(is_ordered(mnas))

        groups = get_groups(mnas)

        self.assertListEqual(expected_groups, groups)

    def test_should_return_molecules_split_by_groups(self):
        mnas = from_file(file_for_test(SAMPLE_MOLECULES_ORDERED_BY_HAND))
        expected_molecules = (from_file(file_for_test(SAMPLE_MOLECULES_ORDERED_BY_HAND1)),
                              from_file(file_for_test(SAMPLE_MOLECULES_ORDERED_BY_HAND2)))

        molecules = get_molecules_by_groups(mnas)

        self.assertTupleEqual(expected_molecules, molecules)

    def test_should_return_groups_when_isolated_cation_present_middle(self):
        mnas_na = from_file(file_for_test(MNAS_NA))
        expected_groups = [[1, 1, 2, 1, 2, 2, 4, 3, 1, 1, 1], [1], [1, 1, 2, 1, 2, 2, 4, 3, 1, 1, 1]]

        self.assertTrue(is_ordered(mnas_na))

        groups = get_groups(mnas_na)

        self.assertListEqual(expected_groups, groups)

    def test_should_return_groups_when_isolated_cation_present_end(self):
        mnas_na = from_file(file_for_test(MNAS_NA2))
        expected_groups = [[1, 1, 2, 1, 2, 2, 4, 3, 1, 1, 1], [1, 1, 2, 1, 2, 2, 4, 3, 1, 1, 1], [1]]

        self.assertTrue(is_ordered(mnas_na))

        groups = get_groups(mnas_na)

        self.assertListEqual(expected_groups, groups)

    def test_should_return_groups_when_isolated_cation_present_beginning(self):
        mnas_na = from_file(file_for_test(MNAS_NA3))
        expected_groups = [[1], [1, 1, 2, 1, 2, 2, 4, 3, 1, 1, 1], [1, 1, 2, 1, 2, 2, 4, 3, 1, 1, 1]]

        self.assertTrue(is_ordered(mnas_na))

        groups = get_groups(mnas_na)

        self.assertListEqual(expected_groups, groups)

    def test_should_return_false_for_molecule_shuffled(self):
        mna = from_file(file_for_test(SAMPLE_SHUFFLED_MOLECULES))

        self.assertFalse(is_ordered(mna))

    def test_should_return_true_for_two_ordered_molecules(self):
        mnas = from_file(file_for_test(SAMPLE_REORDERED_MOLECULES))

        self.assertTrue(is_ordered(mnas))

    def test_should_recalculate_partial_charges(self):
        mnas = from_file(file_for_test(SAMPLE_REORDERED_MOLECULE))

        mnas = get_molecule_with_generated_charges(mnas)

        self.assertAlmostEqual(mnas.get_charge(), 0., places=5)
        self.assertNotEqual(mnas.atoms[0].charge, 0.)

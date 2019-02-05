import os
import unittest

import numpy as np

from chi1chi2.utils.constants import ZERO_TRANSLATION, Symmop
from chi1chi2.utils.molecule import Molecule
from chi1chi2.utils.molecule_reader_writer import from_file


def from_file_os(file):
    return from_file(os.path.join(os.path.dirname(__file__), file))


class TestSymmopTransformer(unittest.TestCase):
    def test_no_change_when_identity_applied(self):
        molecule = from_file_os("mna.xyz")

        transformed = Molecule.transform(molecule, Symmop(np.identity(3), ZERO_TRANSLATION))

        self.assertEqual(molecule, transformed)

    def test_translation_only(self):
        mol = from_file_os("mna.xyz")
        mol_ref = from_file_os("mna_translated.xyz")

        transformed = Molecule.transform(mol, Symmop(np.identity(3), np.array([1, 2, 3]).reshape((3, 1))))

        self.assertEqual(mol_ref, transformed)

    def test_reflection(self):
        mol = from_file_os("mna.xyz")
        mol_ref = from_file_os("mna_reflected_y.xyz")

        transformed = Molecule.transform(mol, Symmop(np.array([1, 0, 0, 0, -1, 0, 0, 0, 1]).reshape((3, 3)),
                                                     ZERO_TRANSLATION))

        self.assertEqual(mol_ref, transformed)

    def test_inversion_and_translation(self):
        mol = from_file_os("mna.xyz")
        mol_ref = from_file_os("mna_inverted_translated.xyz")

        transformed = Molecule.transform(mol, Symmop(np.array([-1, 0, 0, 0, -1, 0, 0, 0, -1]).reshape((3, 3)),
                                                     np.array([1, 2, 3]).reshape((3, 1))))

        self.assertEqual(mol_ref, transformed)

import os
import unittest

from chi1chi2.core.property import DistributedPolar, Polar, Hyper
from chi1chi2.core.property_reader import PropsMol
from chi1chi2.utils.constants import simeq


def file_for_test(file):
    return os.path.join(os.path.dirname(__file__), file)


MOLECULAR_PROPERTIES = file_for_test("prop2.dat")
DISTRIBUTED = file_for_test("dist2.dat")
NUMBER_OF_SUBMOLECULES = 5

properties = PropsMol.from_file(MOLECULAR_PROPERTIES)


class TestDistributed(unittest.TestCase):
    def test_read_polar_from_file(self):
        ref_polarizability = properties.get_or_static("static").polar_w

        distributed = DistributedPolar.from_file(DISTRIBUTED)

        self.assertTrue(all(simeq(ref_polarizability.tensor.reshape(9)[i],
                                  distributed.to_molecular_polar().tensor.reshape(9)[i],
                                  0.3)
                            for i in range(9)))

    def test_splitting_polar(self):
        polarizability = properties.get_or_static("static").polar_w
        expected_submolecule_polarizability = Polar(polarizability.tensor / NUMBER_OF_SUBMOLECULES)

        distributed = polarizability.to_distributed(NUMBER_OF_SUBMOLECULES)

        self.assertEqual(expected_submolecule_polarizability, distributed.polar_list[0])

    def test_spltting_hyperpol(self):
        hyper = properties.get_or_static("static").hyper_w
        expected_submolecule_hyperpol = Hyper(hyper.tensor / NUMBER_OF_SUBMOLECULES)

        distributed = hyper.to_distributed(NUMBER_OF_SUBMOLECULES)

        self.assertEqual(expected_submolecule_hyperpol, distributed.hyper_list[0])

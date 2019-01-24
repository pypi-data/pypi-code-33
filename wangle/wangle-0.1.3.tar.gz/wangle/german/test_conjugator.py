import unittest
import os

from . import conjugator

class Tests(unittest.TestCase):
                        
    def test_model_verb_type(self):
        full_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'test_data', 'model_verb_type.txt')
        with open(full_path) as fin:
            for line in fin:
                if len(line) > 0:
                    lemma, expected_verb_type = line.strip().split(':')
                    verb_type = conjugator.verb_type(lemma)
                    self.assertEqual(verb_type, expected_verb_type)

    def test_model_conjugations_present(self):
        full_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'test_data', 'model_conjugations_present.txt')
        with open(full_path) as fin:
            for line in fin:
                if len(line) > 0:
                    lemma, rest = line.strip().split(':')
                    expected_conjugations = rest.split(',')

                    with self.subTest(lemma=lemma):
                        conjugations = {}
                        for subject_group in ['S1', 'S2', 'S3', 'P1', 'P2', 'P3']:
                            expected = expected_conjugations.pop(0)
                            if expected == '-':
                                continue
                            calculated = conjugator.calculate_present(lemma, subject_group)
                            self.assertEqual(calculated, expected, msg=('the %s conjugation should be %s, not %s' % (subject_group, expected, calculated)))

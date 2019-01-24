import unittest
import os

from .conjugation import Conjugator

class Tests(unittest.TestCase):

    def test_lemma_models(self):
        conjugator = Conjugator()
        full_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'test_data', 'verb_models.txt')
        result = []
        with open(full_path) as fin:
            for line in fin:
                if len(line) > 0:
                    lemma, expected = line.strip().split(',')
                    with self.subTest(lemma=lemma):
                        calculated = conjugator.calculate_lemma_model(lemma)
                        self.assertEqual(expected, calculated, msg=('lemma \'%s\' should have model \'%s\', not model \'%s\'' % (lemma, expected, calculated)))
                        
    def test_model_conjugations_présent(self):
        conjugator = Conjugator()
        full_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'test_data', 'model_conjugations_présent.txt')
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
                            calculated = conjugator.calculate_présent(lemma, subject_group)
                            self.assertEqual(calculated, expected, msg=('the %s conjugation should be %s, not %s' % (subject_group, expected, calculated)))

    def test_model_conjugations_imparfait(self):
        conjugator = Conjugator()
        full_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'test_data', 'model_conjugations_imparfait.txt')
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
                            calculated = conjugator.calculate_imparfait(lemma, subject_group)
                            self.assertEqual(calculated, expected, msg=('the %s conjugation should be %s, not %s' % (subject_group, expected, calculated)))

    def test_model_conjugations_futur(self):
        conjugator = Conjugator()
        full_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'test_data', 'model_conjugations_futur.txt')
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
                            calculated = conjugator.calculate_futur(lemma, subject_group)
                            self.assertEqual(calculated, expected, msg=('the %s conjugation should be %s, not %s' % (subject_group, expected, calculated)))

    def test_model_conjugations_conditionnel(self):
        conjugator = Conjugator()
        full_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'test_data', 'model_conjugations_conditionnel.txt')
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
                            calculated = conjugator.calculate_conditionnel(lemma, subject_group)
                            self.assertEqual(calculated, expected, msg=('the %s conjugation should be %s, not %s' % (subject_group, expected, calculated)))

    def test_model_conjugations_passé_simple(self):
        conjugator = Conjugator()
        full_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'test_data', 'model_conjugations_passé_simple.txt')
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
                            calculated = conjugator.calculate_passé_simple(lemma, subject_group)
                            self.assertEqual(calculated, expected, msg=('the %s conjugation should be %s, not %s' % (subject_group, expected, calculated)))

    def test_model_conjugations_subjonctif_présent(self):
        conjugator = Conjugator()
        full_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'test_data', 'model_conjugations_subjonctif_présent.txt')
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
                            calculated = conjugator.calculate_subjonctif_présent(lemma, subject_group)
                            self.assertEqual(calculated, expected, msg=('the %s conjugation should be %s, not %s' % (subject_group, expected, calculated)))


    def test_model_conjugations_past_participle(self):
        conjugator = Conjugator()
        full_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'test_data', 'model_conjugations_past_participle.txt')
        with open(full_path) as fin:
            for line in fin:
                if len(line) > 0:
                    lemma, rest = line.strip().split(':')
                    expected_conjugations = rest.split(',')

                    with self.subTest(lemma=lemma):
                        conjugations = {}
                        for declension in [(True, False), (False, False), (True, True), (False, True)]:
                            expected = expected_conjugations.pop(0)
                            if expected == '-':
                                continue
                            calculated = conjugator.calculate_past_participle(lemma, declension[0], declension[1])
                            self.assertEqual(calculated, expected, msg=('the conjugation for masculine=%s, plural=%s should be %s, not %s' % (declension[0], declension[1], expected, calculated)))

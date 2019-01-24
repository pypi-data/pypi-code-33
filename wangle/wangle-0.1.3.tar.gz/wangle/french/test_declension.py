import unittest
import os

from wangle.structure import Sentence
from .declension import Decliner
from .pronoun import add_subject_pronoun
from .verb import add_finite_verb
from .adjective import add_adjective

class Tests(unittest.TestCase):
    def test_adjective_inflections(self):
        decliner = Decliner()
        full_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'test_data', 'adjective_declensions.txt')
        with open(full_path) as fin:
            for line in fin:
                if len(line) > 0:
                    declensions = line.strip().split(',')
                    lemma = declensions[0]
                    with self.subTest(lemma=lemma):
                        i = 0
                        for plural in [False, True]:
                            for masculine in [True, False]:
                                expected = declensions[i]
                                calculated = decliner.calculate_declension(lemma, masculine, plural)
                                self.assertEqual(calculated, expected, msg=('the masculine=%s, plural=%s declension should be %s, not %s' % (masculine, plural, expected, calculated)))
                                i += 1

    def test_adjective_derives_declension(self):
        decliner = Decliner()
        for gender in [None, "masc", "fem"]:
            for is_plural in [None, True, False]:
                with self.subTest(gender=gender, is_plural=is_plural):
                    s = Sentence()
                    p = add_subject_pronoun(s, "vous", gender=gender, is_plural=is_plural)
                    if gender is None:
                        self.assertFalse(p.has_tag("gender"))
                    else:
                        self.assertEqual(p.get_tag_value("gender"), gender)
                    if is_plural is None:
                        self.assertFalse(p.has_tag("is_plural"))
                    else:
                        self.assertEqual(p.get_tag_value("is_plural"), is_plural)
                    v = add_finite_verb(s, "être", p.id)
                    adj = add_adjective(s, "content", p.id)

                    calculated_gender = decliner.word_gender(s, adj)
                    if gender is None:
                        self.assertEqual(calculated_gender, "masc")
                    else:
                        self.assertEqual(calculated_gender, gender)

                    calculated_is_plural = decliner.word_is_plural(s, adj)
                    if is_plural is None:
                        self.assertEqual(calculated_is_plural, False)
                    else:
                        self.assertEqual(calculated_is_plural, is_plural)

    def test_adjective_declension(self):
        decliner = Decliner()
        declensions = [
            (None, False, "content"),
            (None, True, "contents"),
            ("masc", None, "content"),
            ("fem", None, "contente"),
            ("masc", False, "content"),
            ("fem", False, "contente"),
            ("masc", True, "contents"),
            ("fem", True, "contentes"),
        ]
        for gender, is_plural, declension in declensions:
            with self.subTest(gender=gender, is_plural=is_plural):
                s = Sentence()
                p = add_subject_pronoun(s, "vous", gender=gender, is_plural=is_plural)
                v = add_finite_verb(s, "être", p.id)
                adj = add_adjective(s, "content", p.id)
                decliner.decline(s, adj)
                self.assertEqual(str(adj), declension)

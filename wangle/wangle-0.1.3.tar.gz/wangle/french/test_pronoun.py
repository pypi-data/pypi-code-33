import unittest

from ..structure import Sentence
from .pronoun import add_subject_pronoun

class Tests(unittest.TestCase):

    def test_subject_pronoun_gender(self):
        pronoun_genders = [
            ('je', None),
            ('tu', None),
            ('il', "masc"),
            ('elle', "fem"),
            ('on', None),
            ('ce', None),
            ('ça', None),
            ('cela', None),
            ('ceci', None),
            ('qui', None),
            ('nous', None),
            ('vous', None),
            ('ils', "masc"),
            ('elles', "fem"),
        ]
        for pronoun, gender in pronoun_genders:
            with self.subTest(pronoun=pronoun):
                s = Sentence()
                p = add_subject_pronoun(s, pronoun)
                if gender is None:
                    self.assertFalse(p.has_tag("gender"))
                else:
                    self.assertEqual(p.get_tag_value("gender"), gender)

    def test_subject_pronoun_plurality(self):
        pronoun_pluralities = [
            ('je', False),
            ('tu', False),
            ('il', False),
            ('elle', False),
            ('on', False),
            ('ce', None),
            ('ça', False),
            ('cela', False),
            ('ceci', False),
            ('nous', True),
            ('vous', None),
            ('ils', True),
            ('elles', True),
        ]
        for pronoun, is_plural in pronoun_pluralities:
            with self.subTest(pronoun=pronoun):
                s = Sentence()
                p = add_subject_pronoun(s, pronoun)
                if is_plural is None:
                    self.assertFalse(p.has_tag("is_plural"))
                else:
                    self.assertEqual(p.get_tag_value("is_plural"), is_plural)


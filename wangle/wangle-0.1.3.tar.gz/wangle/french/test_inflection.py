import unittest

from wangle.structure import Sentence
from .inflection import Inflector
from .pronoun import add_subject_pronoun
from .verb import add_finite_verb
from .adjective import add_adjective

class Tests(unittest.TestCase):

    def test_simple_contraction(self):
        inflector = Inflector()

        s = Sentence()
        p = add_subject_pronoun(s, 'je')
        v = add_finite_verb(s, 'aimer', p.id)
        inflector.inflect(s)
        inflector.contract(s)
        self.assertEqual(str(s), "j'aime")

    def test_adjective_inflection(self):
        inflector = Inflector()
        inflections = [
            (None, False, "vous êtes content"),
            (None, True, "vous êtes contents"),
            ("masc", None, "vous êtes content"),
            ("fem", None, "vous êtes contente"),
            ("masc", False, "vous êtes content"),
            ("fem", False, "vous êtes contente"),
            ("masc", True, "vous êtes contents"),
            ("fem", True, "vous êtes contentes"),
        ]
        for gender, is_plural, inflection in inflections:
            with self.subTest(gender=gender, is_plural=is_plural):
                s = Sentence()
                p = add_subject_pronoun(s, "vous", gender=gender, is_plural=is_plural)
                v = add_finite_verb(s, "être", p.id)
                adj = add_adjective(s, "content", p.id)
                inflector.inflect(s)
                self.assertEqual(str(s), inflection)

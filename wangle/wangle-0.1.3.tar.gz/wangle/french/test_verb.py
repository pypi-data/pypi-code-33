import unittest

from ..structure import Sentence
from .inflection import Inflector
from .pronoun import add_subject_pronoun, add_reflexive_pronoun
from .verb import add_finite_verb

class Tests(unittest.TestCase):
    def test_single_tense_labelling(self):
        inflector = Inflector()
        test_case = [
            ("indicatif", "présent"),
            ("indicatif", "imparfait"),
            ("indicatif", "passé simple"),
            ("indicatif", "futur"),
            ("conditionnel", "présent"),
            ("subjonctif", "présent"),
            ("subjonctif", "imparfait"),
        ]
        for mood, tense in test_case:
            with self.subTest(mood=mood, tense=tense):
                s = Sentence()
                p = add_subject_pronoun(s, "je")
                lemma = "aimer"
                v = add_finite_verb(s, lemma, p.id, mood=mood, tense=tense)
                inflector.inflect(s)

                self.assertEqual(v.lemma, lemma)
                self.assertTrue(v.has_tag("verb"))
                self.assertTrue(v.has_tag("finite_verb"))
                self.assertTrue(v.has_tag("main_verb"))
                self.assertEqual(v.get_tag_value("mood"), mood)
                self.assertEqual(v.get_tag_value("tense"), tense)
                self.assertEqual(v.get_tag_value("conj_mood"), mood)
                self.assertEqual(v.get_tag_value("conj_tense"), tense)

    def test_single_aux_compound_tense_labelling(self):
        inflector = Inflector()
        test_case = [
            ("indicatif", "passé composé", "présent"),
            ("indicatif", "plus-que-parfait", "imparfait"),
            ("indicatif", "passé anterieur", "passé simple"),
            ("indicatif", "futur anterieur", "futur"),
            ("conditionnel", "passé", "présent"),
            ("subjonctif", "passé", "présent"),
            ("subjonctif", "plus-que-parfait", "passé simple"),
        ]
        for mood, tense, aux_tense in test_case:
            with self.subTest(mood=mood, tense=tense):
                s = Sentence()
                p = add_subject_pronoun(s, "je")
                lemma = "aimer"
                v = add_finite_verb(s, lemma, p.id, mood=mood, tense=tense)
                inflector.inflect(s)

                aux = s.tokens[1]
                pp = s.tokens[2]

                self.assertEqual(aux.lemma, "avoir")
                self.assertTrue(aux.has_tag("verb"))
                self.assertTrue(aux.has_tag("finite_verb"))
                self.assertEqual(aux.get_tag_value("conj_mood"), mood)
                self.assertEqual(aux.get_tag_value("conj_tense"), aux_tense)
                self.assertEqual(aux.get_tag_value("aux_for"), pp.id)
                self.assertFalse(aux.has_tag("main_verb"))

                self.assertEqual(pp.lemma, lemma)
                self.assertTrue(pp.has_tag("verb"))
                self.assertTrue(pp.has_tag("main_verb"))
                self.assertEqual(pp.get_tag_value("mood"), mood)
                self.assertEqual(pp.get_tag_value("tense"), tense)
                self.assertTrue(pp.has_tag("past_participle"))
                self.assertFalse(pp.has_tag("finite_verb"))

    def test_vandertramp_verbs_use_être_aux(self):
        inflector = Inflector()
        test_cases = [
            ("indicatif", "passé composé", "présent"),
            ("indicatif", "plus-que-parfait", "imparfait"),
            ("indicatif", "passé anterieur", "passé simple"),
            ("indicatif", "futur anterieur", "futur"),
            ("conditionnel", "passé", "présent"),
            ("subjonctif", "passé", "présent"),
            ("subjonctif", "plus-que-parfait", "passé simple"),
        ]
        vandertramp_lemmas = [
            "devenir", 
            "revenir",
            "monter",
            "rester",
            "sortir",
            "venir",
            "aller",
            "naître",
            "descendre",
            "entrer",
            "retourner",
            "tomber",
            "rentrer",
            "arriver",
            "mourir",
            "partir"
        ]
        for lemma in vandertramp_lemmas:
            for mood, tense, aux_tense in test_cases:
                with self.subTest(mood=mood, tense=tense):
                    s = Sentence()
                    p = add_subject_pronoun(s, "je")
                    v = add_finite_verb(s, lemma, p.id, mood=mood, tense=tense)
                    inflector.inflect(s)

                    aux = s.tokens[1]

                    self.assertEqual(aux.lemma, "être")

    def test_être_aux_override(self):
        inflector = Inflector()
        test_cases = [
            ("indicatif", "passé composé", "présent"),
            ("indicatif", "plus-que-parfait", "imparfait"),
            ("indicatif", "passé anterieur", "passé simple"),
            ("indicatif", "futur anterieur", "futur"),
            ("conditionnel", "passé", "présent"),
            ("subjonctif", "passé", "présent"),
            ("subjonctif", "plus-que-parfait", "passé simple"),
        ]
        for mood, tense, aux_tense in test_cases:
            with self.subTest(mood=mood, tense=tense):
                s = Sentence()
                p = add_subject_pronoun(s, "je")
                v = add_finite_verb(s, "demeurer", p.id, mood=mood, tense=tense)
                inflector.inflect(s)

                aux = s.tokens[1]

                self.assertEqual(aux.lemma, "avoir")
        for mood, tense, aux_tense in test_cases:
            with self.subTest(mood=mood, tense=tense):
                s = Sentence()
                p = add_subject_pronoun(s, "je")
                v = add_finite_verb(s, "demeurer", p.id, mood=mood, tense=tense, aux_lemma="être")
                inflector.inflect(s)

                aux = s.tokens[1]

                self.assertEqual(aux.lemma, "être")

    def test_présent_inflection(self):
        inflector = Inflector()
        conjugations = [
            ("je", "je suis"),
            ("tu", "tu es"),
            ("il", "il est"),
            ("nous", "nous sommes"),
            ("vous", "vous êtes"),
            ("ils", "ils sont"),
        ]
        for subject, conjugation in conjugations:
            with self.subTest(subject=subject):
                s = Sentence()
                p = add_subject_pronoun(s, subject)
                v = add_finite_verb(s, 'être', p.id)
                inflector.inflect(s)
                inflector.contract(s)
                self.assertEqual(str(s), conjugation)

    def test_présent_inflection_reflexive(self):
        inflector = Inflector()
        conjugations = [
            ("je", "je me débrouille"),
            ("tu", "tu te débrouilles"),
            ("il", "il se débrouille"),
            ("nous", "nous nous débrouillons"),
            ("vous", "vous vous débrouillez"),
            ("ils", "ils se débrouillent"),
        ]
        for subject, conjugation in conjugations:
            with self.subTest(subject=subject):
                s = Sentence()
                p = add_subject_pronoun(s, subject)
                r = add_reflexive_pronoun(s, p.id)
                v = add_finite_verb(s, 'débrouiller', p.id, reflexive_pronoun_id=r.id)
                inflector.inflect(s)
                inflector.contract(s)
                self.assertEqual(str(s), conjugation)
                
    def test_imparfait_inflection(self):
        inflector = Inflector()
        conjugations = [
            ("je", "j'étais"),
            ("tu", "tu étais"),
            ("il", "il était"),
            ("nous", "nous étions"),
            ("vous", "vous étiez"),
            ("ils", "ils étaient"),
        ]
        for subject, conjugation in conjugations:
            with self.subTest(subject=subject):
                s = Sentence()
                p = add_subject_pronoun(s, subject)
                v = add_finite_verb(s, 'être', p.id, tense="imparfait")
                inflector.inflect(s)
                inflector.contract(s)
                self.assertEqual(str(s), conjugation)

    def test_imparfait_inflection_reflexive(self):
        inflector = Inflector()
        conjugations = [
            ("je", "je me débrouillais"),
            ("tu", "tu te débrouillais"),
            ("il", "il se débrouillait"),
            ("nous", "nous nous débrouillions"),
            ("vous", "vous vous débrouilliez"),
            ("ils", "ils se débrouillaient"),
        ]
        for subject, conjugation in conjugations:
            with self.subTest(subject=subject):
                s = Sentence()
                p = add_subject_pronoun(s, subject)
                r = add_reflexive_pronoun(s, p.id)
                v = add_finite_verb(s, 'débrouiller', p.id, tense="imparfait", reflexive_pronoun_id=r.id)
                inflector.inflect(s)
                inflector.contract(s)
                self.assertEqual(str(s), conjugation)

    def test_futur_inflection(self):
        inflector = Inflector()
        conjugations = [
            ("je", "je serai"),
            ("tu", "tu seras"),
            ("il", "il sera"),
            ("nous", "nous serons"),
            ("vous", "vous serez"),
            ("ils", "ils seront"),
        ]
        for subject, conjugation in conjugations:
            with self.subTest(subject=subject):
                s = Sentence()
                p = add_subject_pronoun(s, subject)
                v = add_finite_verb(s, 'être', p.id, tense="futur")
                inflector.inflect(s)
                inflector.contract(s)
                self.assertEqual(str(s), conjugation)

    def test_futur_inflection_reflexive(self):
        inflector = Inflector()
        conjugations = [
            ("je", "je me débrouillerai"),
            ("tu", "tu te débrouilleras"),
            ("il", "il se débrouillera"),
            ("nous", "nous nous débrouillerons"),
            ("vous", "vous vous débrouillerez"),
            ("ils", "ils se débrouilleront"),
        ]
        for subject, conjugation in conjugations:
            with self.subTest(subject=subject):
                s = Sentence()
                p = add_subject_pronoun(s, subject)
                r = add_reflexive_pronoun(s, p.id)
                v = add_finite_verb(s, 'débrouiller', p.id, tense="futur", reflexive_pronoun_id=r.id)
                inflector.inflect(s)
                inflector.contract(s)
                self.assertEqual(str(s), conjugation)

    def test_passé_simple_inflection(self):
        inflector = Inflector()
        conjugations = [
            ("je", "je fus"),
            ("tu", "tu fus"),
            ("il", "il fut"),
            ("nous", "nous fûmes"),
            ("vous", "vous fûtes"),
            ("ils", "ils furent"),
        ]
        for subject, conjugation in conjugations:
            with self.subTest(subject=subject):
                s = Sentence()
                p = add_subject_pronoun(s, subject)
                v = add_finite_verb(s, 'être', p.id, tense="passé simple")
                inflector.inflect(s)
                inflector.contract(s)
                self.assertEqual(str(s), conjugation)

    def test_passé_simple_inflection_reflexive(self):
        inflector = Inflector()
        conjugations = [
            ("je", "je me débrouillai"),
            ("tu", "tu te débrouillas"),
            ("il", "il se débrouilla"),
            ("nous", "nous nous débrouillâmes"),
            ("vous", "vous vous débrouillâtes"),
            ("ils", "ils se débrouillèrent"),
        ]
        for subject, conjugation in conjugations:
            with self.subTest(subject=subject):
                s = Sentence()
                p = add_subject_pronoun(s, subject)
                r = add_reflexive_pronoun(s, p.id)
                v = add_finite_verb(s, 'débrouiller', p.id, tense="passé simple", reflexive_pronoun_id=r.id)
                inflector.inflect(s)
                inflector.contract(s)
                self.assertEqual(str(s), conjugation)

    def test_passé_composé_inflection(self):
        inflector = Inflector()
        conjugations = [
            ("je", "j'ai aimé"),
            ("tu", "tu as aimé"),
            ("il", "il a aimé"),
            ("nous", "nous avons aimé"),
            ("vous", "vous avez aimé"),
            ("ils", "ils ont aimé"),
        ]
        for subject, conjugation in conjugations:
            with self.subTest(subject=subject):
                s = Sentence()
                p = add_subject_pronoun(s, subject)
                v = add_finite_verb(s, 'aimer', p.id, tense="passé composé")
                inflector.inflect(s)
                inflector.contract(s)
                self.assertEqual(str(s), conjugation)

    def test_passé_composé_inflection_reflexive(self):
        inflector = Inflector()
        conjugations = [
            ("je", "je me suis débrouillé"),
            ("tu", "tu t'es débrouillé"),
            ("il", "il s'est débrouillé"),
            ("elle", "elle s'est débrouillée"),
            ("nous", "nous nous sommes débrouillés"),
            ("vous", "vous vous êtes débrouillé"),
            ("ils", "ils se sont débrouillés"),
            ("elles", "elles se sont débrouillées"),
        ]
        for subject, conjugation in conjugations:
            with self.subTest(subject=subject):
                s = Sentence()
                p = add_subject_pronoun(s, subject)
                r = add_reflexive_pronoun(s, p.id)
                v = add_finite_verb(s, 'débrouiller', p.id, tense="passé composé", reflexive_pronoun_id=r.id)
                inflector.inflect(s)
                inflector.contract(s)
                self.assertEqual(str(s), conjugation)

    def test_plus_que_parfait_inflection(self):
        inflector = Inflector()
        conjugations = [
            ("je", "j'avais aimé"),
            ("tu", "tu avais aimé"),
            ("il", "il avait aimé"),
            ("nous", "nous avions aimé"),
            ("vous", "vous aviez aimé"),
            ("ils", "ils avaient aimé"),
        ]
        for subject, conjugation in conjugations:
            with self.subTest(subject=subject):
                s = Sentence()
                p = add_subject_pronoun(s, subject)
                v = add_finite_verb(s, 'aimer', p.id, tense="plus-que-parfait")
                inflector.inflect(s)
                inflector.contract(s)
                self.assertEqual(str(s), conjugation)

    def test_plus_que_parfait_inflection_reflexive(self):
        inflector = Inflector()
        conjugations = [
            ("je", "je m'étais débrouillé"),
            ("tu", "tu t'étais débrouillé"),
            ("il", "il s'était débrouillé"),
            ("elle", "elle s'était débrouillée"),
            ("nous", "nous nous étions débrouillés"),
            ("vous", "vous vous étiez débrouillé"),
            ("ils", "ils s'étaient débrouillés"),
            ("elles", "elles s'étaient débrouillées"),
        ]
        for subject, conjugation in conjugations:
            with self.subTest(subject=subject):
                s = Sentence()
                p = add_subject_pronoun(s, subject)
                r = add_reflexive_pronoun(s, p.id)
                v = add_finite_verb(s, 'débrouiller', p.id, tense="plus-que-parfait", reflexive_pronoun_id=r.id)
                inflector.inflect(s)
                inflector.contract(s)
                self.assertEqual(str(s), conjugation)

    def test_futur_anterieur_inflection(self):
        inflector = Inflector()
        conjugations = [
            ("je", "j'aurai aimé"),
            ("tu", "tu auras aimé"),
            ("il", "il aura aimé"),
            ("nous", "nous aurons aimé"),
            ("vous", "vous aurez aimé"),
            ("ils", "ils auront aimé"),
        ]
        for subject, conjugation in conjugations:
            with self.subTest(subject=subject):
                s = Sentence()
                p = add_subject_pronoun(s, subject)
                v = add_finite_verb(s, 'aimer', p.id, tense="futur anterieur")
                inflector.inflect(s)
                inflector.contract(s)
                self.assertEqual(str(s), conjugation)

    def test_futur_anterieur_inflection_reflexive(self):
        inflector = Inflector()
        conjugations = [
            ("je", "je me serai débrouillé"),
            ("tu", "tu te seras débrouillé"),
            ("il", "il se sera débrouillé"),
            ("elle", "elle se sera débrouillée"),
            ("nous", "nous nous serons débrouillés"),
            ("vous", "vous vous serez débrouillé"),
            ("ils", "ils se seront débrouillés"),
            ("elles", "elles se seront débrouillées"),
        ]
        for subject, conjugation in conjugations:
            with self.subTest(subject=subject):
                s = Sentence()
                p = add_subject_pronoun(s, subject)
                r = add_reflexive_pronoun(s, p.id)
                v = add_finite_verb(s, 'débrouiller', p.id, tense="futur anterieur", reflexive_pronoun_id=r.id)
                inflector.inflect(s)
                inflector.contract(s)
                self.assertEqual(str(s), conjugation)

    def test_passé_anterieur_inflection(self):
        inflector = Inflector()
        conjugations = [
            ("je", "j'eus aimé"),
            ("tu", "tu eus aimé"),
            ("il", "il eut aimé"),
            ("nous", "nous eûmes aimé"),
            ("vous", "vous eûtes aimé"),
            ("ils", "ils eurent aimé"),
        ]
        for subject, conjugation in conjugations:
            with self.subTest(subject=subject):
                s = Sentence()
                p = add_subject_pronoun(s, subject)
                v = add_finite_verb(s, 'aimer', p.id, tense="passé anterieur")
                inflector.inflect(s)
                inflector.contract(s)
                self.assertEqual(str(s), conjugation)

    def test_passé_anterieur_inflection_reflexive(self):
        inflector = Inflector()
        conjugations = [
            ("je", "je me fus débrouillé"),
            ("tu", "tu te fus débrouillé"),
            ("il", "il se fut débrouillé"),
            ("elle", "elle se fut débrouillée"),
            ("nous", "nous nous fûmes débrouillés"),
            ("vous", "vous vous fûtes débrouillé"),
            ("ils", "ils se furent débrouillés"),
            ("elles", "elles se furent débrouillées"),
        ]
        for subject, conjugation in conjugations:
            with self.subTest(subject=subject):
                s = Sentence()
                p = add_subject_pronoun(s, subject)
                r = add_reflexive_pronoun(s, p.id)
                v = add_finite_verb(s, 'débrouiller', p.id, tense="passé anterieur", reflexive_pronoun_id=r.id)
                inflector.inflect(s)
                inflector.contract(s)
                self.assertEqual(str(s), conjugation)

    def test_conditionnel_présent_inflection(self):
        inflector = Inflector()
        conjugations = [
            ("je", "je serais"),
            ("tu", "tu serais"),
            ("il", "il serait"),
            ("nous", "nous serions"),
            ("vous", "vous seriez"),
            ("ils", "ils seraient"),
        ]
        for subject, conjugation in conjugations:
            with self.subTest(subject=subject):
                s = Sentence()
                p = add_subject_pronoun(s, subject)
                v = add_finite_verb(s, 'être', p.id, mood="conditionnel")
                inflector.inflect(s)
                inflector.contract(s)
                self.assertEqual(str(s), conjugation)

    def test_conditionnel_présent_inflection_reflexive(self):
        inflector = Inflector()
        conjugations = [
            ("je", "je me débrouillerais"),
            ("tu", "tu te débrouillerais"),
            ("il", "il se débrouillerait"),
            ("nous", "nous nous débrouillerions"),
            ("vous", "vous vous débrouilleriez"),
            ("ils", "ils se débrouilleraient"),
        ]
        for subject, conjugation in conjugations:
            with self.subTest(subject=subject):
                s = Sentence()
                p = add_subject_pronoun(s, subject)
                r = add_reflexive_pronoun(s, p.id)
                v = add_finite_verb(s, 'débrouiller', p.id, mood="conditionnel", reflexive_pronoun_id=r.id)
                inflector.inflect(s)
                inflector.contract(s)
                self.assertEqual(str(s), conjugation)

    def test_conditionnel_passé_inflection(self):
        inflector = Inflector()
        conjugations = [
            ("je", "j'aurais aimé"),
            ("tu", "tu aurais aimé"),
            ("il", "il aurait aimé"),
            ("nous", "nous aurions aimé"),
            ("vous", "vous auriez aimé"),
            ("ils", "ils auraient aimé"),
        ]
        for subject, conjugation in conjugations:
            with self.subTest(subject=subject):
                s = Sentence()
                p = add_subject_pronoun(s, subject)
                v = add_finite_verb(s, 'aimer', p.id, mood="conditionnel", tense="passé")
                inflector.inflect(s)
                inflector.contract(s)
                self.assertEqual(str(s), conjugation)

    def test_conditionnel_passé_inflection_reflexive(self):
        inflector = Inflector()
        conjugations = [
            ("je", "je me serais débrouillé"),
            ("tu", "tu te serais débrouillé"),
            ("il", "il se serait débrouillé"),
            ("elle", "elle se serait débrouillée"),
            ("nous", "nous nous serions débrouillés"),
            ("vous", "vous vous seriez débrouillé"),
            ("ils", "ils se seraient débrouillés"),
            ("elles", "elles se seraient débrouillées"),
        ]
        for subject, conjugation in conjugations:
            with self.subTest(subject=subject):
                s = Sentence()
                p = add_subject_pronoun(s, subject)
                r = add_reflexive_pronoun(s, p.id)
                v = add_finite_verb(s, 'débrouiller', p.id, mood="conditionnel", tense="passé", reflexive_pronoun_id=r.id)
                inflector.inflect(s)
                inflector.contract(s)
                self.assertEqual(str(s), conjugation)

    def test_subjonctif_présent_inflection(self):
        inflector = Inflector()
        conjugations = [
            ("je", "je sois"),
            ("tu", "tu sois"),
            ("il", "il soit"),
            ("nous", "nous soyons"),
            ("vous", "vous soyez"),
            ("ils", "ils soient"),
        ]
        for subject, conjugation in conjugations:
            with self.subTest(subject=subject):
                s = Sentence()
                p = add_subject_pronoun(s, subject)
                v = add_finite_verb(s, 'être', p.id, mood="subjonctif")
                inflector.inflect(s)
                inflector.contract(s)
                self.assertEqual(str(s), conjugation)

    def test_subjonctif_présent_inflection_reflexive(self):
        inflector = Inflector()
        conjugations = [
            ("je", "je me débrouille"),
            ("tu", "tu te débrouilles"),
            ("il", "il se débrouille"),
            ("nous", "nous nous débrouillions"),
            ("vous", "vous vous débrouilliez"),
            ("ils", "ils se débrouillent"),
        ]
        for subject, conjugation in conjugations:
            with self.subTest(subject=subject):
                s = Sentence()
                p = add_subject_pronoun(s, subject)
                r = add_reflexive_pronoun(s, p.id)
                v = add_finite_verb(s, 'débrouiller', p.id, mood="subjonctif", reflexive_pronoun_id=r.id)
                inflector.inflect(s)
                inflector.contract(s)
                self.assertEqual(str(s), conjugation)

    def test_subjonctif_passé_inflection(self):
        inflector = Inflector()
        conjugations = [
            ("je", "j'aie aimé"),
            ("tu", "tu aies aimé"),
            ("il", "il ait aimé"),
            ("nous", "nous ayons aimé"),
            ("vous", "vous ayez aimé"),
            ("ils", "ils aient aimé"),
        ]
        for subject, conjugation in conjugations:
            with self.subTest(subject=subject):
                s = Sentence()
                p = add_subject_pronoun(s, subject)
                v = add_finite_verb(s, 'aimer', p.id, mood="subjonctif", tense="passé")
                inflector.inflect(s)
                inflector.contract(s)
                self.assertEqual(str(s), conjugation)

    def test_subjonctif_passé_inflection_reflexive(self):
        inflector = Inflector()
        conjugations = [
            ("je", "je me sois débrouillé"),
            ("tu", "tu te sois débrouillé"),
            ("il", "il se soit débrouillé"),
            ("elle", "elle se soit débrouillée"),
            ("nous", "nous nous soyons débrouillés"),
            ("vous", "vous vous soyez débrouillé"),
            ("ils", "ils se soient débrouillés"),
            ("elles", "elles se soient débrouillées"),
        ]
        for subject, conjugation in conjugations:
            with self.subTest(subject=subject):
                s = Sentence()
                p = add_subject_pronoun(s, subject)
                r = add_reflexive_pronoun(s, p.id)
                v = add_finite_verb(s, 'débrouiller', p.id, mood="subjonctif", tense="passé", reflexive_pronoun_id=r.id)
                inflector.inflect(s)
                inflector.contract(s)
                self.assertEqual(str(s), conjugation)

    def test_past_participle_agrees_with_subject_for_transitive_conjugation_with_etre_aux(self):
        inflector = Inflector()
        declensions = [
            (None, False, "vous êtes allé"),
            (None, True, "vous êtes allés"),
            ("masc", None, "vous êtes allé"),
            ("fem", None, "vous êtes allée"),
            ("masc", False, "vous êtes allé"),
            ("fem", False, "vous êtes allée"),
            ("masc", True, "vous êtes allés"),
            ("fem", True, "vous êtes allées"),
        ]
        for gender, is_plural, result in declensions:
            with self.subTest(gender=gender, is_plural=is_plural):
                s = Sentence()
                p = add_subject_pronoun(s, "vous", gender=gender, is_plural=is_plural)
                v = add_finite_verb(s, "aller", p.id, tense="passé composé")
                inflector.inflect(s)
                self.assertEqual(str(s), result)

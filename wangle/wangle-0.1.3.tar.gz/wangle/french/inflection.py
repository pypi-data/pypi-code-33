from wangle import structure

from .conjugation import Conjugator
from .declension import Decliner
from . import adjective
from . import verb
from .helper import causes_elision_in_preceding_word

class Inflector(structure.Sentence):
    def __init__(self, conjugator=None, decliner=None):
        super().__init__()

        if conjugator is None:
            self.conjugator = Conjugator()
        else:
            self.conjugator = conjugator

        if decliner is None:
            self.decliner = Decliner()
        else:
            self.decliner = decliner

    def inflect(self, sentence, save_parameters=True):
        for token in sentence.tokens:
            if isinstance(token, structure.Word):
                word = token
                if word.has_tag("adjective"):
                    self.decliner.decline(sentence, word, save_parameters)
                if word.has_tag("verb"):
                    self.conjugator.conjugate(sentence, word, save_parameters)

    def contract(self, sentence):
        i = 0
        while i < len(sentence.tokens) - 1:
            token = sentence.tokens[i]
            next_token = sentence.tokens[i + 1]
            if isinstance(token, structure.Word) and isinstance(next_token, structure.Word) and str(token) in ["je", "me", "te", "se", "le", "la", "que"] and causes_elision_in_preceding_word(str(next_token)):
                token.inflection = token.inflection[0:-1]
                sentence.tokens.insert(i + 1, "'")
            i += 1

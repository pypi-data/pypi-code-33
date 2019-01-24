def render_tokens(tokens):
    result = ""
    for i, token in enumerate(tokens):
        # add space between two words
        if i > 0 and isinstance(token, Word) and isinstance(tokens[i - 1], Word):
            result += " "
        result += str(token)

    return result

class Tag:
    def __init__(self, tag_name, value=None):
        self.tag_name = tag_name
        self.value = value

    def clone(self):
        return Tag(self.name, complement=self.complement)

class Word:    
    def __init__(self, id, lemma):
        self.id = id
        self.lemma = lemma
        self.inflection = lemma 
        self.tags = {}

    def set_tag(self, tag_name, value=None):
        self.tags[tag_name] = Tag(tag_name, value)

    def has_tag(self, tag_name):
        return tag_name in self.tags

    def get_tag_value(self, tag_name):
        return self.tags[tag_name].value

    def __str__(self):
        return self.inflection

class Sentence:
    def __init__(self):
        self._word_id_seed = 1
        self.tokens = []
        self.words = {}

    def register_word(self, lemma):
        word = Word(self._word_id_seed, lemma)
        self.words[word.id] = word
        self._word_id_seed += 1
        return word

    def find_words_by_tag(self, tag_name, value=None):
        result = []
        for word in self.words.values():
            if tag_name in word.tags:
                if value is None or value == word.tags[tag_name].value:
                    result.append(word)
                    break
        return result


    def __str__(self):
        return render_tokens(self.tokens)

    def __repr__(self):
        result = ""
        for i, token in enumerate(self.tokens):
            if isinstance(token, Word):
                result += "{}: {} -> {}\n".format(token.id, token.lemma, token.inflection)
                for tag_name in token.tags:
                    if token.tags[tag_name].value is None:
                        result += "\t{}\n".format(tag_name)
                    else:
                        result += "\t{}: {}\n".format(tag_name, token.tags[tag_name].value)
            else:
                result += "{}\n".format(token)
        return result

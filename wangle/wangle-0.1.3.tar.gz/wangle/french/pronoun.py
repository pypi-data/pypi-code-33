def add_subject_pronoun(sentence, lemma, gender=None, is_plural=None, position=None):
    word = sentence.register_word(lemma)

    word.set_tag("pronoun")

    if lemma in ["il", "ils"]:
        word.set_tag("gender", value="masc")
    elif lemma in ["elle", "elles"]:
        word.set_tag("gender", value="fem")
    elif gender is not None:
        word.set_tag("gender", value=gender)

    if lemma in ["je", "tu", "il", "elle", "on", "ça", "cela", "ceci"]:
        word.set_tag("is_plural", value=False)
    elif lemma in ["nous", "ils", "elles"]:
        word.set_tag("is_plural", value=True)
    elif is_plural is not None:
        word.set_tag("is_plural", value=is_plural)

    if position is not None:
        sentence.tokens.insert(position, word)
    else:
        sentence.tokens.append(word)

    return word

def add_reflexive_pronoun(sentence, subject_id, position=None):
    subject = sentence.words[subject_id]

    lemma = None
    if subject.lemma == 'je':
        lemma = 'me'
    elif subject.lemma == 'tu':
        lemma = 'te'
    elif subject.lemma == 'nous':
        lemma = 'nous'
    elif subject.lemma == 'vous':
        lemma = 'vous'
    if subject.lemma in ["il", "elle", "on", "ça", "cela", "ceci", "ce", "ils", "elles"]:
        lemma = 'se'

    word = None
    if lemma is not None:
        word = sentence.register_word(lemma)
        word.set_tag("pronoun")
        word.set_tag("agrees_with", subject_id)
        if position is not None:
            sentence.tokens.insert(position, word)
        else:
            sentence.tokens.append(word)

    return word

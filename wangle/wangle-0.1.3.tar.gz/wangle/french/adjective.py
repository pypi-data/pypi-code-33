def add_adjective(sentence, lemma, nominal_word_id, position=None):
    word = sentence.register_word(lemma)

    word.set_tag("adjective")
    word.set_tag("modifies", nominal_word_id)
    word.set_tag("agrees_with", nominal_word_id)

    if position is not None:
        sentence.tokens.insert(position, word)
    else:
        sentence.tokens.append(word)

    return word


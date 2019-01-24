verbs_that_conjugate_with_etre = [
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

def add_finite_verb(sentence, lemma, subject_id, mood="indicatif", tense="présent", informal=False, position=None, aux_lemma=None, reflexive_pronoun_id=None):
    verb = sentence.register_word(lemma)

    verb.set_tag("verb")
    verb.set_tag("main_verb")
    verb.set_tag("mood", value=mood)
    verb.set_tag("tense", value=tense)

    if informal:
        verb.set_tag("informal")

    aux, finite_verb, pp = None, None, None

    if mood == "indicatif":
        if tense in ["présent", "imparfait", "passé simple", "futur"]:
            verb.set_tag("conj_mood", value=mood)
            verb.set_tag("conj_tense", value=tense)
            finite_verb = verb
        if tense in ["passé composé", "plus-que-parfait", "passé anterieur", "futur anterieur"]:
            if aux_lemma is None:
                if verb.lemma in verbs_that_conjugate_with_etre or reflexive_pronoun_id is not None:
                    aux_lemma = "être"
                else:
                    aux_lemma = "avoir"
            aux = sentence.register_word(aux_lemma)
            aux.set_tag("verb")
            aux.set_tag("conj_mood", value=mood)
            aux_tense = None
            if tense == "passé composé":
                aux_tense = "présent"
            elif tense == "plus-que-parfait":
                aux_tense = "imparfait"
            elif tense == "passé anterieur":
                aux_tense = "passé simple"
            elif tense == "futur anterieur":
                aux_tense = "futur"
            aux.set_tag("conj_tense", value=aux_tense)
            aux.set_tag("aux_for", value=verb.id)
            finite_verb = aux 
            verb.set_tag("past_participle")
            pp = verb
    elif mood == "conditionnel":
        if tense in ["présent"]:
            verb.set_tag("conj_mood", value=mood)
            verb.set_tag("conj_tense", value=tense)
            finite_verb = verb
        if tense == "passé":
            if aux_lemma is None:
                if verb.lemma in verbs_that_conjugate_with_etre or reflexive_pronoun_id is not None:
                    aux_lemma = "être"
                else:
                    aux_lemma = "avoir"
            aux = sentence.register_word(aux_lemma)
            aux.set_tag("verb")
            aux.set_tag("conj_mood", value=mood)
            aux.set_tag("conj_tense", value="présent")
            aux.set_tag("aux_for", value=verb.id)
            finite_verb = aux 
            verb.set_tag("past_participle")
            pp = verb
    elif mood == "subjonctif":
        if tense in ["présent", "imparfait"]:
            verb.set_tag("conj_mood", value=mood)
            verb.set_tag("conj_tense", value=tense)
            finite_verb = verb
        if tense in ["passé", "plus-que-parfait"]:
            if aux_lemma is None:
                if verb.lemma in verbs_that_conjugate_with_etre or reflexive_pronoun_id is not None:
                    aux_lemma = "être"
                else:
                    aux_lemma = "avoir"
            aux = sentence.register_word(aux_lemma)
            aux.set_tag("verb")
            aux.set_tag("conj_mood", value=mood)
            aux_tense = None
            if tense == "passé":
                aux_tense = "présent"
            elif tense == "plus-que-parfait":
                aux_tense = "passé simple"
            aux.set_tag("conj_tense", value=aux_tense)
            aux.set_tag("aux_for", value=verb.id)
            finite_verb = aux 
            verb.set_tag("past_participle")
            pp = verb

    if aux is not None:
        if position is not None:
            sentence.tokens.insert(position, aux)
            position += 1
        else:
            sentence.tokens.append(aux)

    if position is not None:
        sentence.tokens.insert(position, verb)
    else:
        sentence.tokens.append(verb)

    if finite_verb is not None:
        subj = sentence.words[subject_id]
        subj.set_tag("subject_for", verb.id)
        finite_verb.set_tag("finite_verb")
        finite_verb.set_tag("agrees_with", subj.id)

    if pp is not None and aux.lemma == "être":
        if reflexive_pronoun_id is not None:
            pp.set_tag("agrees_with", reflexive_pronoun_id)
        else:
            pp.set_tag("agrees_with", subj.id)

    return verb


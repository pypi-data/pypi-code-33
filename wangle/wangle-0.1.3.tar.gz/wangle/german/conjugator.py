def calculate_infinitive_stem(lemma):
    if lemma.endswith('en'):
        return lemma[:-2]
    elif lemma.endswith('n'): 
        return lemma[:-1]

def calculate_lemma_model(lemma):
    if lemma == 'sein':
        return 'sein'
    elif lemma == 'haben':
        return 'haben'
    elif lemma == 'werden':
        return 'werden'
    elif lemma.endswith('ten'):
        return 'warten' 
    elif lemma.endswith('en'):
        return 'kaufen' 
    else:
        return 'wandern' 

def verb_type(model):
    if model in ['kaufen', 'warten', 'wandern']:
        return 'weak'
    else:
        return 'strong'

def calculate_present_stem(lemma, model, subject_group):
    stem = calculate_infinitive_stem(lemma)
    if model == 'haben' and subject_group in ['S2', 'S3']:
        stem = stem[:-1]
    elif model == 'werden':
        if subject_group == 'S2':
            stem = 'wir'
        elif subject_group == 'S3':
            stem = 'wird'
        else:
            stem = 'werd'
    return stem 

def calculate_present_suffix(model, subject_group):
    suffix = None

    # Weak conjugation
    if subject_group == 'S1':
        suffix = 'e'
    elif subject_group == 'S2':
        suffix = 'st'
    elif subject_group in ['S3', 'P2']:
        suffix = 't'
    elif subject_group in ['P1', 'P3']:
        suffix = 'en'

    if model == 'warten' and subject_group in ['S2', 'S3', 'P2']:
        suffix = 'e' + suffix
    elif model == 'wandern' and suffix == 'en':
        suffix = 'n'

    # Strong/mixed conjugation
    if model == 'werden' and subject_group == 'P2':
        suffix = 'e' + suffix

    return suffix

def calculate_present(lemma, subject_group):
    model = calculate_lemma_model(lemma)

    # Exceptions
    if model == 'sein':
        if subject_group == 'S1':
            return 'bin'
        elif subject_group == 'S2':
            return 'bist'
        elif subject_group == 'S3':
            return 'ist'
        elif subject_group == 'P2':
            return 'seid'
        elif subject_group in ['P1', 'P3']:
            return 'sind'

    stem = calculate_present_stem(lemma, model, subject_group)
    if stem is None:
        return None

    suffix = calculate_present_suffix(model, subject_group)
    if suffix is None:
        return None

    if stem.endswith('d') and suffix == 't':
        suffix = ''

    result = stem + suffix

    return result

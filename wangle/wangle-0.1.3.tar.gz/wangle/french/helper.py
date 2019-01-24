def is_vowel(letter):
    return letter.lower() in 'aâeéèêiîïoôuy'

def starts_with_mute_h(word):
    return word.lower().startswith('h') and not starts_with_aspirated_h(word)

def starts_with_aspirated_h(word):
    return word.lower().startswith('hiéro')

def causes_elision_in_preceding_word(word):
    return is_vowel(word[0]) or starts_with_mute_h(word)

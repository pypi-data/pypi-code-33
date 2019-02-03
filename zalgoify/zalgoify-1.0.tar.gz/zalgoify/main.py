import random


DIACRITICS_TOP = [' ̍',' ̎',' ̄',' ̅',' ̿',' ̑',' ̆',' ̐',' ͒',' ͗',' ͑',' ̇',' ̈',' ̊',' ͂',' ̓',' ̈́',' ͊',' ͋',' ͌',' ̃',' ̂',' ̌',' ͐',' ́',' ̋',' ̏',' ̽',' ̉',' ͣ',' ͤ',' ͥ',' ͦ',' ͧ',' ͨ',' ͩ',' ͪ',' ͫ',' ͬ',' ͭ',' ͮ',' ͯ',' ̾',' ͛',' ͆',' ̚',]
DIACRITICS_MIDDLE = [' ̕',' ̛',' ̀',' ́',' ͘',' ̡',' ̢',' ̧',' ̨',' ̴',' ̵',' ̶',' ͜',' ͝',' ͞',' ͟',' ͠',' ͢',' ̸',' ̷',' ͡',]
DIACRITICS_BOTTOM = ['̖',' ̗',' ̘',' ̙',' ̜',' ̝',' ̞',' ̟',' ̠',' ̤',' ̥',' ̦',' ̩',' ̪',' ̫',' ̬',' ̭',' ̮',' ̯',' ̰',' ̱',' ̲',' ̳',' ̹',' ̺',' ̻',' ̼',' ͅ',' ͇',' ͈',' ͉',' ͍',' ͎',' ͓',' ͔',' ͕',' ͖',' ͙',' ͚',' ',]

def process(text: str, min_top_diacritics=1, max_top_diacritics=3, min_middle_diacritics=1, max_middle_diacritics=2, min_bottom_diacritics=1, max_bottom_diacritics=3, remove_spaces=False):
    """
    Add zalgo characters to a string.
    """
    output = ''

    # Add diacritics for each character
    for character in text:
        # If character is not alphabetical, skip it
        if not character.isalpha():
            output += character
            continue

        num_top_diacritics = random.randint(min_top_diacritics, max_top_diacritics)
        num_bottom_diacritics = random.randint(min_bottom_diacritics, max_bottom_diacritics)
        num_middle_diacritics = random.randint(min_middle_diacritics, max_middle_diacritics)
        for i in range(num_top_diacritics):
            character = mark(character, DIACRITICS_TOP)
        for i in range(num_middle_diacritics):
            character = mark(character, DIACRITICS_MIDDLE)
        for i in range(num_bottom_diacritics):
            character = mark(character, DIACRITICS_BOTTOM)

        output += character

    if remove_spaces:
        output.replace(' ', '')

    return output

def strip(text: str):
    """
    Remove diacritics from text.
    """
    for diacritic in DIACRITICS_TOP + DIACRITICS_MIDDLE + DIACRITICS_BOTTOM:
        text = text.replace(diacritic.strip(), '')
    return text

def mark(character, diacritic_options):
    """
    Combine character with a random diacritic.
    """
    return character + random.choice(diacritic_options).strip()

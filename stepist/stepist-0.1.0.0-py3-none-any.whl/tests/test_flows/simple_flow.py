from collections import Counter
from stepist import step


STOP_WORDS = ['a', 'the', 'on', 'at']


@step(None)
def return_amount_of_the(counter):
    return dict(the=counter['the'])


@step(return_amount_of_the)
def calculate_amount_of_stop_words(words):
    return dict(counts=Counter(words))


@step(calculate_amount_of_stop_words)
def split_by_words(text):
    return dict(words=text.split(' '),
                text=text)


@step(split_by_words)
def read_text(file):
    with open(file, "r") as f:
        return dict(text=f.read())
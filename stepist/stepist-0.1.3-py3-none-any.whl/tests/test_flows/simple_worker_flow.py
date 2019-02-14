from collections import Counter
from stepist import step

from stepist.tests import utils

STOP_WORDS = ['a', 'the', 'on', 'at']


@step(None, as_worker=True)
def save_to_redis(the):
    utils.save_test_result(dict(the=the))


@step(save_to_redis)
def return_amount_of_the(counter):
    return dict(the=counter['the'])


@step(return_amount_of_the, as_worker=True)
def calculate_amount_of_stop_words(words):
    return dict(counts=Counter(words))


@step(calculate_amount_of_stop_words, as_worker=True)
def split_by_words(text):
    return dict(words=text.split(' '),
                text=text)


@step(split_by_words)
def read_text(file):
    with open(file, "r") as f:
        return dict(text=f.read())
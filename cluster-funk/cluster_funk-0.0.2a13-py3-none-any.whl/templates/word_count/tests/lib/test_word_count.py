import unittest
import os
from lib.word_count import word_count


def fixture(file_name):
    return os.path.join(os.path.dirname(__file__), os.pardir, 'fixtures', file_name)


class TestWordCount(unittest.TestCase):

    def test_word_count(self):
        expected = [('hello', 3), ('world', 1), ('hello.', 1), ('', 2), ('Are', 1),
                    ('you', 1), ('good?', 1), ('I', 2), ('know', 1), ('am', 1)]
        output = word_count(fixture("words.txt"))
        assert expected == output

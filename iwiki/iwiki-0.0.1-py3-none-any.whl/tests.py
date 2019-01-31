import unittest

from .wiki import *


class ExistanceTestCase(unittest.TestCase):

    def test_valid_search(self):
        existed = search_existance(word='data science', lang='en')
        self.assertEqual(existed, True)

    def test_invalid_word_search(self):
        existed = search_existance(word='date science', lang='en')
        self.assertEqual(existed, False)

    # 언어영역과 단어의 언어종류를 서로 다르게.
    def test_unmatched_search(self):
        existed = search_existance(word='data science', lang='ko')
        self.assertEqual(existed, False)

    def test_invalid_requests(self):
        existed = search_existance(word='data science', lang='')
        self.assertEqual(existed, None)

def main():
    unittest.main()

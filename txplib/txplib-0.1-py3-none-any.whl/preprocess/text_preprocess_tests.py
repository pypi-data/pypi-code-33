import unittest
from txplib.preprocess import *

from tests.library import nlp_library_tests


class TestPreprocessor(unittest.TestCase):

    def setUp(self):
        self.mocked_library_behaviour_dict = dict()

        def tokenize_sentence(text):
            if text is None or text == '':
                return []
            elif text == "She likes dogs. Food is awesome! We went to library.":
                return ["She", "likes", "dogs", "Food", "awesome", "!", "We", "Went", "to", "library", "."]

            raise ValueError

        def tokenize_words(sentence):
            if sentence is None or sentence == "":
                return []

        def lemmatize(word):
            if word == "likes":
                return "like"
            elif word == "dogs":
                return "dog"
            elif word == "is":
                return "be"
            elif word == 'went':
                return "go"
            else:
                return word

        stopwords = {"she", "be", "we", "to"}

        self.mocked_library_behaviour_dict['sentence_tokenizer'] = tokenize_sentence
        self.mocked_library_behaviour_dict['word_tokenizer'] = tokenize_words
        self.mocked_library_behaviour_dict['stopword'] = stopwords
        self.mocked_library_behaviour_dict["lemmatizer"] = lemmatize

        self.library = nlp_library_tests.MockedNLPLibrary(self.mocked_library_behaviour_dict)


    def test_sentence_tokenizer_empty_case(self):
        text1 = ""

        sent_tok = SentenceTokenizer(self.library)

        self.assertEqual(
            [],
            sent_tok.transform(text1)
        )

        word_tok = WordTokenizer(self.library)
        self.assertEqual(
            [[]],
            word_tok.transform([])
        )

    def test_normalizer(self):
        text = ['she', 'likes', 'dogs', 'food', 'is', 'awesome', 'we', 'went', 'to', 'library']

        doc_bow = Lemmatizer(self.library)

        self.assertEqual(
            [['she', 'like', 'dog', 'food', 'be', 'awesome', 'we', 'go', 'to', 'library'],
             ['she', 'like', 'dog', 'food', 'be', 'awesome', 'we', 'go', 'to', 'library']],
            doc_bow.transform([text, text])
        )

    def test_stopwords_filter(self):
        text = ['she', 'like', 'dog', 'food', 'be', 'awesome', 'we', 'go', 'to', 'library']

        doc_bow = TokenFilter(self.library, "stopword")

        self.assertEqual(
            [['like', 'dog', 'food', 'awesome', 'go', 'library'],
             ['like', 'dog', 'food', 'awesome', 'go', 'library']],
            doc_bow.transform([text, text])
        )
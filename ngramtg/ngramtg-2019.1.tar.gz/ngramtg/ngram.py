from ngramtg.exceptions import \
    AccessViolationException, \
    InvalidCorpusFile, \
    NoCorpus, \
    NoUnprocessedCorpus

import random
import os.path


class NgramTextGen:
    def __init__(self, corpus_file=None, ngram_length=2, auto=False):
        self.__ngram_length = ngram_length

        if corpus_file:
            self.set_corpus_filename(corpus_file)
        else:
            self.__corpus_filename = None

        if auto:
            self.setup_everything()
        else:
            self.__unprocessed_corpus = None
            self.__corpus = None
            self.__ngrams = None
            self.__frequency_map = None

        self.__sentence = None

    def __repr__(self):
        return (f"{self.__class__.__name__}("
                f"Corpus file: {self.corpus_filename()}, "
                f"Length: {self.__ngram_length})")

    def setup_everything(self, corpus=None):
        """Convenience function that sets up all properties of the object."""
        if not corpus and not self.corpus_filename():
            raise NoCorpus("Cannot setup without corpus or a corpus file.")
        if not corpus:
            corpus = self.read_corpus_file(self.corpus_filename())
        self.set_unprocessed_corpus(corpus)
        corpus = self.add_structural_tokens(corpus)
        corpus = self.preprocess_corpus(corpus)
        corpus = self.tokenize(corpus)
        self.set_corpus(corpus)
        ngrams = self.create_ngrams(corpus, n=self.ngram_length())
        self.set_ngrams(ngrams)
        self.set_frequency_map(self.generate_word_frequency_map(ngrams))

    def ngram_length(self):
        """Get the n-gram length."""
        return self.__ngram_length

    def set_ngram_length(self, n=None):
        """Set the n-gram length."""
        if not n:
            return
        if n <= 0:
            raise ValueError("Length `n` must be a positive number.")
        self.__ngram_length = n

    def corpus_filename(self):
        """Returns the corpus file name."""
        return self.__corpus_filename

    def set_corpus_filename(self, filename=None):
        """Sets `corpus_file` to `filename` if the file exists, else `None`."""
        if not filename:
            return
        if os.path.exists(filename):
            self.__corpus_filename = filename
        else:
            raise InvalidCorpusFile

    @staticmethod
    def read_corpus_file(filename=None):
        """Returns the contents of the given `filename`."""
        if not filename:
            return
        with open(filename) as corpus_file:
            corpus = corpus_file.read().splitlines()
        return corpus

    def corpus(self):
        """Returns the corpus."""
        return self.__corpus

    def set_corpus(self, corpus=None):
        """Set the corpus."""
        if not corpus:
            return
        if type(corpus) != list:
            raise AccessViolationException
        self.__corpus = corpus

    def unprocessed_corpus(self):
        """Unprocessed corpus getter method."""
        return self.__unprocessed_corpus

    def set_unprocessed_corpus(self, unprocessed_corpus=None):
        """Unprocessed corpus setter method"""
        if not unprocessed_corpus:
            return
        self.__unprocessed_corpus = unprocessed_corpus

    def ngrams(self):
        """Returns the instance's ngrams."""
        return self.__ngrams

    def set_ngrams(self, ngrams=None):
        """Set the ngrams."""
        if not ngrams:
            return
        self.__ngrams = ngrams

    def frequency_map(self):
        """Frequency map getter."""
        return self.__frequency_map

    def set_frequency_map(self, frequency_map=None):
        """Frequency map setter."""
        if not frequency_map:
            return None
        self.__frequency_map = frequency_map

    def sentence(self):
        """Sentence getter."""
        if not self.__sentence:
            self.set_sentence(self.create_sentence(self.frequency_map()))
        return self.__sentence

    def set_sentence(self, sentence=None):
        if not sentence:
            return None
        self.__sentence = sentence

    @staticmethod
    def add_structural_tokens(unprocessed_corpus=None):
        """Add START and END tokens to a line of text."""
        if not unprocessed_corpus:
            raise NoUnprocessedCorpus("Cannot add structural tokens.")
        corpus = []
        for entry in unprocessed_corpus:
            corpus.append("::START " + entry + " ::END")

        return corpus

    def is_duplicate(self, sentence, a_list=None):
        """Returns true if `sentence` occurs in `a_list`."""
        if a_list:
            lst = a_list
        elif self.unprocessed_corpus():
            lst = self.unprocessed_corpus()
        else:
            return False
        for entry in lst:
            if sentence == entry:
                return True
        return False

    @staticmethod
    def create_ngrams(token_list=None, n=2):
        """Creates n-grams of length n. Returns bigrams by default."""
        if not token_list:
            return None
        ngrams = []
        for token in range(len(token_list) - n + 1):
            ngrams.append(token_list[token:token + n])

        return ngrams

    @staticmethod
    def preprocess_corpus(corpus=None):
        """Removes newlines and adds padding to punctuation characters."""
        if not corpus:
            return

        for index, entry in enumerate(corpus):
            entry = entry.replace(",", " ,")
            entry = entry.replace(".", " .")
            entry = entry.replace("?", " ?")
            entry = entry.replace("!", " !")
            corpus[index] = entry
        return corpus

    @staticmethod
    def tokenize(corpus=None):
        if not corpus:
            return None
        split_corpus = []
        for entry in corpus:
            split_corpus.append(entry.split())

        # Return a flattened list
        return [y for x in split_corpus for y in x]

    def create_sentence(self, frequency_map=None):
        """Create a random sentence from given ngrams."""
        if not frequency_map:
            if not self.frequency_map():
                return None
            else:
                frequency_map = self.frequency_map()
        tokens = []

        bad = [" ", ",", ".", "?", "!", "::START"]
        end_tokens = [".", "!", "::END"]
        sentence = ""
        first_word = True

        token = random.choice(list(frequency_map["::START"].keys()))
        while token != "::END":
            if token not in bad and not first_word:
                tokens.append(" ")
            tokens.append(token)
            first_word = False
            if token in end_tokens:
                break
            token = random.choice(list(frequency_map[token].keys()))

        for entry in tokens:
            sentence += entry

        self.set_sentence(sentence)
        return sentence

    @staticmethod
    def generate_word_frequency_map(ngrams=None):
        """Returns a dictionary of dictionaries with counts of next words."""
        word_frequencies = {}

        for ngram in ngrams:
            length = len(ngram) - 1

            for pos in range(length):
                this_token = ngram[pos]
                next_token = ngram[pos + 1]

                if this_token not in word_frequencies:
                    word_frequencies[this_token] = {}

                if next_token not in word_frequencies[this_token]:
                    word_frequencies[this_token][next_token] = 0
                word_frequencies[this_token][next_token] += 1

        return word_frequencies

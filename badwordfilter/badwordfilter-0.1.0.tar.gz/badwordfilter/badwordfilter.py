# -*- coding: utf-8 -*-

import re
import os

import inflection
from django.conf import settings

class BadWordFilter:
    def __init__(self, **kwargs):

        # If defined, use this instead of _censor_list
        self._custom_censor_list = kwargs.get('custom_censor_list', [])

        # Words to be used in conjunction with _censor_list
        self._extra_censor_list = kwargs.get('extra_censor_list', [])

        # What to be censored -- should not be modified by user
        self._censor_list = []

        # What to censor the words with
        self._censor_char = "*"

        # Where to find the censored words
        self._BASE_DIR = os.path.abspath(os.path.dirname(__file__))
        self._words_file = os.path.join(self._BASE_DIR, 'wordlist.txt')

        self._load_words()

    def _load_words(self):
        """ Loads the list of bad words from file. """
        with open(self._words_file, 'r') as f:
            self._censor_list = [line.strip() for line in f.readlines()]

    def define_words(self, word_list):
        """ Define a custom list of bad words. """
        self._custom_censor_list = word_list

    def append_words(self, word_list):
        """ Extends the bad word list with word_list """
        self._extra_censor_list.extend(word_list)

    def set_censor(self, character):
        """ Replaces the original censor character '*' with character """
        if isinstance(character, int):
            character = str(character)
        self._censor_char = character

    def has_bad_word(self, text):
        """ Returns True if text contains profanity, False otherwise """
        return self.censor(text) != text

    def get_custom_censor_list(self):
        """ Returns the list of custom bad words """
        return self._custom_censor_list

    def get_extra_censor_list(self):
        """ Returns the list of custom, additional, bad words """
        return self._extra_censor_list

    def get_bad_words(self):
        """ Gets all bad words """
        bad_words = []

        if self._custom_censor_list:
            bad_words = [w for w in self._custom_censor_list]  # Previous versions of Python don't have list.copy()
        else:
            bad_words = [w for w in self._censor_list]

        bad_words.extend(self._extra_censor_list)
        bad_words.extend([inflection.pluralize(word) for word in bad_words])
        bad_words = list(set(bad_words))

        return bad_words

    def restore_words(self):
        """ Clears all custom censor lists """
        self._custom_censor_list = []
        self._extra_censor_list = []

    def censor(self, input_text):
        """ Returns input_text with any bad words censored """
        bad_words = self.get_bad_words()
        res = input_text

        for word in bad_words:
            word = r'\b%s\b' % word  # Apply word boundaries to the bad word
            regex = re.compile(word, re.IGNORECASE)
            res = regex.sub(self._censor_char * (len(word) - 4), res)

        return res

    def is_clean(self, input_text):
        """ Returns True if input_text doesn't contain any bad words, False otherwise. """
        return not self.has_bad_word(input_text)

    def is_bad(self, input_text):
        """ Returns True if input_text contains any bad words, False otherwise. """
        return self.has_bad_word(input_text)

# -*- coding: utf-8 -*-
"""Test Tagger class"""

import os
import pickle
import unittest

from torch_tagger import Tagger
from torch_tagger.utils import text_reader

CURRENT = os.path.realpath(os.path.dirname(__file__))
PATH = os.path.join(CURRENT, 'train.txt')


class TestTagger(unittest.TestCase):
    def test_tagger(self):
        """Test tagger entry"""
        x_data, y_data = text_reader(PATH)
        tagger = Tagger(batch_size=2, epochs=10, verbose=0)
        params = tagger.get_params(True)
        tagger.set_params(**params)

        tagger.fit(x_data, y_data)
        with open('/tmp/test_tagger.pkl', 'wb') as fobj:
            pickle.dump(tagger, fobj)
        with open('/tmp/test_tagger.pkl', 'rb') as fobj:
            tagger = pickle.load(fobj)
        tagger.predict(x_data)
        tagger.predict(x_data, verbose=1)
        tagger.score(x_data, y_data)
        tagger.score(x_data, y_data, verbose=1)

    def test_device(self):
        for device in ('auto', 'gpu', 'cpu'):
            Tagger(device=device)
        with self.assertRaises(AssertionError):
            Tagger(device='unk')

    def test_optimizer(self):
        with self.assertRaises(AssertionError):
            Tagger(optimizer='not_support')


if __name__ == '__main__':
    unittest.main()

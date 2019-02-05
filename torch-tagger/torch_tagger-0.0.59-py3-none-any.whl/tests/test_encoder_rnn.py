# -*- coding: utf-8 -*-
"""Test utils class"""

import unittest

import numpy as np
from torch_tagger.encoder_rnn import EncoderRNN
from torch_tagger.torch_lm import START_TAG, STOP_TAG


class TestUtil(unittest.TestCase):
    def test_constructor(self):
        tag_to_ix = {
            'a': 0,
            'b': 1,
            START_TAG: 2,
            STOP_TAG: 3,
        }
        with self.assertRaises(Exception):
            EncoderRNN(10, tag_to_ix, 10, 10, 1, True, 0., 0., 'invalid', True,
                       'lstm', 10)

    def test_load_embedding(self):
        tag_to_ix = {
            'a': 0,
            'b': 1,
            START_TAG: 2,
            STOP_TAG: 3,
        }
        vocab_size = 10
        embedding_dim = 10
        encoder = EncoderRNN(vocab_size, tag_to_ix, embedding_dim, 10, 1, True,
                             0., 0., 'lstm', True, 'lstm', 10)
        pretrained = np.random.uniform(-1, 1, (vocab_size, embedding_dim))
        encoder.load_embedding(pretrained)
        encoder_embedding = encoder._word_embeds.weight.cpu().detach().numpy()
        self.assertLess(np.sum((encoder_embedding - pretrained)**2), 1e-10)


if __name__ == '__main__':
    unittest.main()

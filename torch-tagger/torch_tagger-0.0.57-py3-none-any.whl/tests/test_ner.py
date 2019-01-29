# -*- coding: utf-8 -*-
"""Test NER"""

import unittest

from torch_tagger import Tagger
from torch_tagger.utils import text_reader


class TestNER(unittest.TestCase):
    def test_train_ner(self):
        """Train NER model"""
        x_data, y_data = text_reader('./tests/train.txt')
        x_val, y_val = text_reader('./tests/train.txt')
        tag = Tagger(
            embedding_dim=100,
            hidden_dim=100,
            weight_decay=1e-8,
            epochs=20,
            verbose=1,
            batch_size=2,
            device='auto',
            embedding_dropout_p=0.5,
            rnn_dropout_p=0.5,
            bidirectional=True,
            rnn_type='lstm',
            num_layers=1,
            optimizer='SGD',
            learning_rate=0.015,
            learning_rate_decay=0.05,
            embedding_trainable=True,
            use_crf=False,
            use_char='cnn',
            char_max_len=50,
            char_embedding_dim=30,
            char_hidden_dim=50,
            char_dropout_p=0.5,
            char_bidirectional=True,
            clip_grad_norm=None,
        )
        tag.fit(
            x_data,
            y_data,
            x_val,
            y_val,
            predict_batch_size=2,
            save_best='/tmp/test.model')


if __name__ == '__main__':
    unittest.main()

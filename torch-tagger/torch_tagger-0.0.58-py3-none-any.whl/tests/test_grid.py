# -*- coding: utf-8 -*-
"""Test Entry"""

import os
import unittest

import torch
from sklearn.model_selection import GridSearchCV
from torch_tagger import Tagger
from torch_tagger.utils import DEVICE, text_reader

CURRENT = os.path.realpath(os.path.dirname(__file__))
PATH = os.path.join(CURRENT, 'train.txt')


class TestGrid(unittest.TestCase):
    def test_grid(self):
        """Test GridSearch"""
        x_data, y_data = text_reader(PATH)
        x_train = x_data + x_data + x_data
        y_train = y_data + y_data + y_data
        parameters = [{
            'bidirectional': (True, False),
            'rnn_type': ('lstm', 'gru'),
        }, {
            'num_layers': (1, 2),
        }, {
            'use_char': ('cnn', 'rnn', None),
        }, {
            'use_crf': (True, False),
        }, {
            'average_loss': (True, False),
        }, {
            'learning_rate': (None, 0.1),
        }, {
            'optimizer': ('sgd', 'adam'),
        }]
        for i, parameter in enumerate(parameters):
            print('test grid {}'.format(i + 1))
            tag = Tagger(batch_size=2, epochs=1, verbose=0, device='cpu')
            clf = GridSearchCV(tag, parameter, verbose=0, n_jobs=1, cv=2)
            clf.fit(x_train, y_train)
            self.assertIsInstance(clf.cv_results_['mean_test_score'][0], float)

    def test_device(self):
        tagger = Tagger(device='cpu')
        self.assertEqual(tagger._get_device(), torch.device('cpu'))
        tagger = Tagger(device='gpu')
        self.assertEqual(tagger._get_device(), torch.device('cuda'))
        tagger = Tagger(device='cuda')
        self.assertEqual(tagger._get_device(), torch.device('cuda'))
        tagger = Tagger(device='auto')
        self.assertEqual(tagger._get_device(), DEVICE)


if __name__ == '__main__':
    unittest.main()

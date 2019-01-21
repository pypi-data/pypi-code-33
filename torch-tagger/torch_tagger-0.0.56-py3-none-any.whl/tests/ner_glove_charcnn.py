# -*- coding: utf-8 -*-
"""Test NER with GloVe

Download https://nlp.stanford.edu/projects/glove/
"""

import os
import random
import tempfile
import uuid

import numpy as np
import torch
from torch_tagger import Tagger
from torch_tagger.utils import PAD_TAG, UNK_TAG, build_vocabulary, text_reader

from .ner import generate_result_ner, test_ner

SEED = 222
random.seed(SEED)
torch.manual_seed(SEED)
torch.cuda.manual_seed(SEED)
np.random.seed(SEED)


def read_glove(train_txt='/tmp/train.txt',
               glove_path='tests/glove.6B/glove.6B.100d.txt',
               dim=100):
    """Reade GloVe vector"""

    x_data, y_data = text_reader(train_txt)
    x_val, y_val = text_reader('/tmp/valid.txt')
    x_test, y_test = text_reader('/tmp/test.txt')
    vocabulary = build_vocabulary(x_data + x_val + x_test,
                                  y_data + y_val + y_test)

    def random_vec():
        return np.random.uniform(
            -np.sqrt(3. / dim), np.sqrt(3. / dim), size=(1, dim))

    def zero_vec():
        return np.zeros((1, dim))

    predefine_vecs = {}
    with open(glove_path, 'r') as fobj:
        lines = fobj.read().split('\n')
        lines = [x.strip() for x in lines]
        lines = [x for x in lines if x.strip()]
        for line in lines:
            line = line.split()
            if len(line) > dim:
                word = line[0]
                vec = np.array([float(i) for i in line[1:]])
                vec = vec.reshape(1, dim)
                predefine_vecs[word] = vec
    vecs = [
        zero_vec(),
        random_vec(),
    ]
    word_to_ix = {PAD_TAG: 0, UNK_TAG: 1}
    perfect = 0
    fuzzy = 0
    none = 0
    for word in vocabulary['word_to_ix']:
        if word not in word_to_ix:
            indx = len(word_to_ix)
            word_to_ix[word] = indx
            if word in predefine_vecs:
                vecs.append(predefine_vecs[word])
                perfect += 1
            elif word.lower() in predefine_vecs:
                vecs.append(predefine_vecs[word.lower()])
                fuzzy += 1
            elif word.upper() in predefine_vecs:
                vecs.append(predefine_vecs[word.upper()])
                fuzzy += 1
            else:
                vecs.append(random_vec())
                none += 1

    ix_to_word = {v: k for k, v in word_to_ix.items()}
    embedding = np.concatenate(vecs)

    print('perfect: {}, fuzz: {}, none: {}'.format(perfect, fuzzy, none))

    return word_to_ix, ix_to_word, embedding


def train_ner():
    """Train NER model"""
    x_data, y_data = text_reader('/tmp/train.txt')
    x_val, y_val = text_reader('/tmp/valid.txt')
    word_to_ix, ix_to_word, embedding = read_glove()
    dropout = 0.5
    tag = Tagger(
        embedding_dim=100,
        hidden_dim=200,
        weight_decay=1e-9,
        epochs=100,
        verbose=1,
        batch_size=10,
        device='auto',
        embedding_dropout_p=dropout,
        rnn_dropout_p=dropout,
        bidirectional=True,
        rnn_type='lstm',
        num_layers=1,
        optimizer='SGD',
        learning_rate=0.005,
        learning_rate_decay=0.02,
        embedding_trainable=True,
        use_crf=True,
        use_char='cnn',
        char_max_len=50,
        char_embedding_dim=100,
        char_hidden_dim=200,
        char_dropout_p=dropout,
        char_bidirectional=True,
        clip_grad_norm=None,
        _word_to_ix=word_to_ix,
        _ix_to_word=ix_to_word)
    print('tag model', tag)

    tag_best_path = os.path.join(tempfile.gettempdir(),
                                 str(uuid.uuid4()) + '.pkl')
    print('tag_best_path', tag_best_path)

    tag.fit(
        x_data,
        y_data,
        x_val,
        y_val,
        patient_dev=20,
        save_best=tag_best_path,
        pretrained_embedding=embedding)

    score = tag.score(x_data, y_data, verbose=1)
    print('train score', score)
    test_ner(tag_best_path)
    generate_result_ner(tag_best_path, tag_best_path + '.txt')


if __name__ == '__main__':
    train_ner()

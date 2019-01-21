# -*- coding: utf-8 -*-
"""Test NER"""

import os
import pickle
import random
import tempfile
import uuid

import numpy as np
import torch
from sklearn.model_selection import train_test_split
from torch_tagger import Tagger
from torch_tagger.utils import PAD_TAG, UNK_TAG, build_vocabulary, text_reader

SEED = 1337
random.seed(SEED)
torch.manual_seed(SEED)
torch.cuda.manual_seed(SEED)
np.random.seed(SEED)


def read_glove(train_txt='/tmp/train.txt',
               glove_path='tests/glove_chinese_char.txt',
               dim=100):
    """Reade GloVe vector"""

    x_data, y_data = text_reader('/tmp/msr_train.txt')
    x_val, y_val = text_reader('/tmp/msr_test.txt')
    vocabulary = build_vocabulary(x_data + x_val, y_data + y_val)

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
    x_data, y_data = text_reader('/tmp/msr_train.txt')
    word_to_ix, ix_to_word, embedding = read_glove()
    tag = Tagger(
        embedding_dim=100,
        hidden_dim=256,
        weight_decay=1e-8,
        epochs=500,
        verbose=1,
        batch_size=20,
        device='auto',
        embedding_dropout_p=0.2,
        rnn_dropout_p=0.2,
        bidirectional=True,
        rnn_type='lstm',
        num_layers=1,
        optimizer='SGD',
        momentum=0.95,
        learning_rate=0.02,  # 0.02,
        learning_rate_decay=0.0,  # 0.05,
        embedding_trainable=True,
        use_crf=False,
        use_char=None,
        # char_max_len=10,
        # char_embedding_dim=64,
        # char_hidden_dim=64,
        # char_dropout_p=0.2,
        # char_bidirectional=True,
        clip_grad_norm=1.,
        average_loss=True,
        _word_to_ix=word_to_ix,
        _ix_to_word=ix_to_word)
    print('tag model', tag)

    tag_best_path = os.path.join(tempfile.gettempdir(),
                                 str(uuid.uuid4()) + '.pkl')
    print('tag_best_path', tag_best_path)
    x_train, x_test, y_train, y_test = train_test_split(
        x_data, y_data, test_size=0.1, random_state=SEED)
    tag.fit(
        x_train,
        y_train,
        x_test,
        y_test,
        save_best=tag_best_path,
        pretrained_embedding=embedding,
        patient_dev=20)
    # with open(tag_best_path, 'wb') as fobj:
    #     pickle.dump(tag, fobj)
    test_ner(tag_best_path)
    generate_result_ner(tag_best_path, tag_best_path + '.txt')


def test_ner(model_path):
    """Test Segmentation model"""
    x_data, y_data = text_reader('/tmp/msr_test.txt')
    print('load model', model_path)
    tag = pickle.load(open(model_path, 'rb'))
    pre, rec, f1s = tag.score(x_data, y_data, verbose=1, detail=True)
    print('test precision {:.4f} recall {:.4f} f1 {:.4f}'.format(
        pre, rec, f1s))
    pred = tag.predict(x_data[:3])

    for i, indy in enumerate(y_data[:3]):
        print(indy)
        print(pred[i])
        print('-' * 30)


def generate_result_ner(model_path,
                        output_path,
                        test_input='/tmp/msr_test.txt'):
    """Generate file could evel by conll eval script"""
    x_data, _ = text_reader(test_input)
    print('load model', model_path)
    tag = pickle.load(open(model_path, 'rb'))
    pred = tag.predict(x_data)
    with open(output_path, 'w') as fobj:
        lines = open(test_input).read().split('\n\n')
        lines = [x.strip() for x in lines]
        lines = [x for x in lines if len(x) > 0]
        for line, line_pred in zip(lines, pred):
            line = [x.split()[0] for x in line.split('\n')]
            line_ret = ''
            for l, p in zip(line, line_pred):
                line_ret += l
                if p in ('E', 'S'):
                    line_ret += ' '
            fobj.write(line_ret + '\n')


if __name__ == '__main__':
    train_ner()

# -*- coding: utf-8 -*-
"""Main tagger class
"""

import io
import math
import os
import pickle

import numpy as np
import pandas as pd
import torch
from sklearn.base import BaseEstimator
from torch import nn, optim
from tqdm import tqdm

from .tagger_dataset import data_iter
from .tagger_model import TaggerModel
from .torch_lm import LanguageModel
from .utils import DEVICE, extract_entities


class Tagger(BaseEstimator):
    """Scikit-learn compatible Tagger

    :param int embedding_dim: 默认100，默认的embedding维度
    :param int hidden_dim: 默认200，隐藏层神经元数量
    :param float weight_decay: 默认0.0，是否使用权重衰竭，理论上可以避免过拟合，参考值如0.001
    :param int epochs: 默认100，训练次数
    :param int verbose: 默认1，训练是否输出进度，0为关闭
    :param int batch_size: 默认32，一个训练批次的大小
    :param str device: 默认'auto'，默认设备，参考值：auto，cpu，gpu，如果是auto，那么会自动选择gpu或cpu
    :param float embedding_dropout_p: 默认0.0，
        默认embedding层的dropout，理论上增加可以避免过拟合，参考值如0.1
    :param float rnn_dropout_p: 默认0.0，rnn层的dropout，理论上增加可以避免过拟合，参考值如0.1
    :param bool bidirectional: 默认True，是否是双向rnn
    :param str rnn_type: 默认'lstm'，rnn类型，lstm or gru
    :param int num_layers: 默认1，encoder的层数
    :param str optimizer: 默认'Adam'，优化器
    :param float momentum: 默认0，如果是SGD优化器，则可选momentum
    :param float learning_rate: 默认None，学习率
    :param float learning_rate_decay: 默认0，学习率衰减
    :param bool embedding_trainable: 默认True，emebedding层是否是要训练的
    :param bool use_crf: 默认True，是否应用CRF的decoder
    :param int max_len: 默认500，最大长度
    :param str use_char: 默认'cnn'，是否使用字符特征，可能的值有：rnn，cnn，None
    :param int char_max_len: 默认50，字符特征最大长度（例如一个单词最大长度）
    :param int char_embedding_dim: 默认30，字符特征embedding维度
    :param int char_hidden_dim: 默认50，字符特征隐藏层神经元数量
    :param float char_dropout_p: 默认0.5，字符特征的dropout
    :param bool char_bidirectional: 默认True，字符特征是否使用bidirectional
    :param float clip_grad_norm: 默认None，是否使用梯度剪裁
    :param bool average_loss: 默认False，是否损失按照batch_size取均值
    """

    def __init__(self,
                 embedding_dim=100,
                 hidden_dim=100,
                 weight_decay=0.0,
                 epochs=100,
                 verbose=1,
                 batch_size=32,
                 device='auto',
                 embedding_dropout_p=0.0,
                 rnn_dropout_p=0.0,
                 bidirectional=True,
                 rnn_type='lstm',
                 num_layers=1,
                 optimizer='Adam',
                 momentum=0,
                 learning_rate=None,
                 learning_rate_decay=0,
                 embedding_trainable=True,
                 use_crf=True,
                 max_len=500,
                 use_char='cnn',
                 char_max_len=50,
                 char_embedding_dim=30,
                 char_hidden_dim=50,
                 char_dropout_p=0.5,
                 char_bidirectional=True,
                 clip_grad_norm=None,
                 average_loss=False,
                 _model=None,
                 _optimizer=None,
                 _word_to_ix=None,
                 _ix_to_word=None,
                 _char_to_ix=None,
                 _ix_to_char=None,
                 _sentence_lm=None,
                 _tag_lm=None):
        """init"""
        assert optimizer.lower() in ('sgd', 'adam')
        assert device.lower() in ('cpu', 'gpu', 'cuda', 'auto')
        self.params = {
            'embedding_dim': embedding_dim,
            'hidden_dim': hidden_dim,
            'weight_decay': weight_decay,
            'epochs': epochs,
            'verbose': verbose,
            'batch_size': batch_size,
            'device': device,
            'embedding_dropout_p': embedding_dropout_p,
            'rnn_dropout_p': rnn_dropout_p,
            'bidirectional': bidirectional,
            'rnn_type': rnn_type,
            'num_layers': num_layers,
            'optimizer': optimizer,
            'momentum': momentum,
            'learning_rate': learning_rate,
            'learning_rate_decay': learning_rate_decay,
            'embedding_trainable': embedding_trainable,
            'use_crf': use_crf,
            'use_char': use_char,
            'max_len': max_len,
            'char_max_len': char_max_len,
            'char_embedding_dim': char_embedding_dim,
            'char_hidden_dim': char_hidden_dim,
            'char_dropout_p': char_dropout_p,
            'char_bidirectional': char_bidirectional,
            'clip_grad_norm': clip_grad_norm,
            'average_loss': average_loss,
        }
        self._sentence_lm = LanguageModel(
            use_char=True if use_char in ('rnn', 'cnn') else False,
            max_len=max_len,
            char_max_len=char_max_len,
            char_pad_method='right' if use_char == 'rnn' else 'both',
            _word_to_ix=_word_to_ix,
            _ix_to_word=_ix_to_word,
            _char_to_ix=_char_to_ix,
            _ix_to_char=_ix_to_char,
        )
        self._tag_lm = LanguageModel(limit=0, use_char=False)
        self._model = _model
        self._optimizer = _optimizer
        if _sentence_lm is not None:
            self._sentence_lm = _sentence_lm
        if _tag_lm is not None:
            self._tag_lm = _tag_lm

    def _get_learning_rate(self):
        """default learning rate"""
        optimizer = self.params['optimizer']
        learning_rate = self.params['learning_rate']
        if learning_rate is not None:
            return learning_rate
        if optimizer.lower() == 'sgd':
            return 1e-2
        if optimizer.lower() == 'adam':
            return 1e-3

    def get_params(self, deep=True):
        """Get params for scikit-learn compatible"""
        params = self.params
        params['_sentence_lm'] = self._sentence_lm
        params['_tag_lm'] = self._tag_lm
        if deep:
            params['_model'] = self._model.state_dict(
            ) if self._model is not None else None
            params['_optimizer'] = self._optimizer.state_dict() \
                if self._optimizer is not None else None
        return params

    def set_params(self, **parameters):
        """Set params for scikit-learn compatible"""
        for key, value in parameters.items():
            if key in self.params:
                self.params[key] = value
            if key == '_sentence_lm':
                self._sentence_lm = value
            if key == '_tag_lm':
                self._tag_lm = value
        return self

    def __getstate__(self):
        """Get state for pickle"""
        _model = None
        if self._model is not None:
            _model = io.BytesIO()
            torch.save(self._model, _model)
            _model.seek(0)

        _optimizer = None
        if self._optimizer is not None:
            _optimizer = io.BytesIO()
            torch.save(self._optimizer, _optimizer)
            _optimizer.seek(0)

        state = {
            'params': self.params,
            '_model': _model,
            # self._model.state_dict() if self._model is not None else None,
            '_optimizer': _optimizer,
            # self._optimizer.state_dict()
            # if self._optimizer is not None else None,
            '_sentence_lm': self._sentence_lm,
            '_tag_lm': self._tag_lm
        }
        return state

    def __setstate__(self, state):
        """Get state for pickle"""
        self.params = state['params']
        if self.params['device'].lower() in (
                'gpu', 'cuda') and not torch.cuda.is_available():
            self.params['device'] = 'auto'
        self._sentence_lm = state['_sentence_lm']
        self._tag_lm = state['_tag_lm']
        if state['_model'] is not None:
            self.apply_params()
            if isinstance(state['_model'], io.BytesIO):
                self._model = torch.load(state['_model'], self._get_device())
                self._optimizer = torch.load(state['_optimizer'],
                                             self._get_device())
            else:  # Legacy 老格式
                self._model.load_state_dict(state['_model'])
                self._optimizer.load_state_dict(state['_optimizer'])

    def _get_device(self):
        """Get device to predict or train"""
        device = self.params['device']
        if device == 'auto':
            return DEVICE
        if device in ('cpu', ):
            return torch.device('cpu')
        if device in ('gpu', 'cuda'):
            return torch.device('cuda')

    def apply_params(self):
        """Apply params and build RNN-CRF model"""

        embedding_dim = self.params['embedding_dim']
        hidden_dim = self.params['hidden_dim']
        weight_decay = self.params['weight_decay']
        embedding_dropout_p = self.params['embedding_dropout_p']
        rnn_dropout_p = self.params['rnn_dropout_p']
        bidirectional = self.params['bidirectional']
        rnn_type = self.params['rnn_type']
        num_layers = self.params['num_layers']
        optimizer = self.params['optimizer']
        momentum = self.params['momentum']
        embedding_trainable = self.params['embedding_trainable']
        use_crf = self.params['use_crf']
        use_char = self.params['use_char']
        char_max_len = self.params['char_max_len']
        char_embedding_dim = self.params['char_embedding_dim']
        char_hidden_dim = self.params['char_hidden_dim']
        char_dropout_p = self.params['char_dropout_p']
        char_bidirectional = self.params['char_bidirectional']
        average_loss = self.params['average_loss']

        model = TaggerModel(
            len(self._sentence_lm.word_to_ix),
            self._tag_lm.word_to_ix,
            embedding_dim,
            hidden_dim,
            num_layers=num_layers,
            bidirectional=bidirectional,
            embedding_dropout_p=embedding_dropout_p,
            rnn_dropout_p=rnn_dropout_p,
            rnn_type=rnn_type,
            embedding_trainable=embedding_trainable,
            use_crf=use_crf,
            use_char=use_char,
            char_max_len=char_max_len,
            char_embedding_dim=char_embedding_dim,
            char_vocab_size=(len(self._sentence_lm.char_to_ix)
                             if self._sentence_lm.use_char else
                             self._sentence_lm.char_max_len),
            char_hidden_dim=char_hidden_dim,
            char_dropout_p=char_dropout_p,
            char_bidirectional=char_bidirectional,
            average_loss=average_loss).to(self._get_device())

        if optimizer.lower() == 'adam':
            optimizer = optim.Adam(
                model.parameters(),
                lr=self._get_learning_rate(),
                weight_decay=weight_decay)
        elif optimizer.lower() == 'sgd':
            optimizer = optim.SGD(
                model.parameters(),
                lr=self._get_learning_rate(),
                weight_decay=weight_decay,
                momentum=momentum)

        self._model = model
        self._optimizer = optimizer

    def fit(self,
            X,
            y,
            X_dev=None,
            y_dev=None,
            patient_dev=None,
            save_best=None,
            pretrained_embedding=None,
            predict_batch_size=32):
        """Fit the model"""

        assert len(X) >= self.params['batch_size'], 'X must size >= batch_size'
        assert len(y) >= self.params['batch_size'], 'y must size >= batch_size'
        assert len(X) == len(y), 'X must size equal to y'

        # Autommatic build vocabulary
        if isinstance(pretrained_embedding, str):
            assert os.path.exists(pretrained_embedding), \
                'Invalid pretrained embedding'
            pretrained_embedding = self._sentence_lm.fit_pretrained(
                pretrained_embedding)
        else:
            self._sentence_lm.fit(X)
        self._tag_lm.fit(y)

        epochs = self.params['epochs']
        verbose = self.params['verbose']
        batch_size = self.params['batch_size']
        learning_rate_decay = self.params['learning_rate_decay']
        # char_max_len = self.params['char_max_len']
        clip_grad_norm = self.params['clip_grad_norm']
        average_loss = self.params['average_loss']

        predict_batch_size = max(predict_batch_size, batch_size)
        if X_dev is not None:
            predict_batch_size = min(predict_batch_size, len(X_dev))

        self.apply_params()
        model, optimizer = self._model, self._optimizer
        if pretrained_embedding is not None:
            model.load_embedding(pretrained_embedding)

        dev_best = float('inf')
        dev_best_round = 0
        # Make sure prepare_sequence from earlier in the LSTM section is loaded
        for epoch in range(epochs):
            model.train()
            model.zero_grad()
            lnrt = self._get_learning_rate()
            if learning_rate_decay > 0:
                lnrt = lnrt / (1 + epoch * learning_rate_decay)
                for param_group in optimizer.param_groups:
                    param_group['lr'] = lnrt

            pbar = data_iter(X, y, self.params['max_len'], self._sentence_lm,
                             self._tag_lm, batch_size)

            losses = []
            if verbose > 0:
                pbar = tqdm(pbar, ncols=0)
                pbar.set_description('epoch: {}/{} loss: {:.4f}'.format(
                    epoch + 1, epochs, 0))

            for x_b, y_b, l_b, l_c, ll_c in pbar:
                x_b = torch.from_numpy(x_b).to(self._get_device())
                y_b = torch.from_numpy(y_b).to(self._get_device())
                l_b = torch.from_numpy(l_b).to(self._get_device())
                if l_c is not None:
                    l_c = torch.from_numpy(l_c).to(self._get_device())
                    ll_c = torch.from_numpy(ll_c).to(self._get_device())
                optimizer.zero_grad()
                loss = model.compute_loss(
                    x_b, y_b, l_b, chars=l_c, charlens=ll_c)
                loss.backward()
                if clip_grad_norm is not None:
                    nn.utils.clip_grad_norm_(model.parameters(),
                                             clip_grad_norm)
                optimizer.step()
                losses.append(loss.detach().item())
                if verbose > 0:
                    pbar.set_description(
                        'epoch: {}/{} loss: {:.4f} lr: {:.4f}'.format(
                            epoch + 1, epochs, np.mean(losses), lnrt))

            if X_dev is not None:
                model.eval()
                with torch.no_grad():
                    dev_score = self.score_table(
                        X_dev, y_dev, batch_size=predict_batch_size)

                    pbar = data_iter(X_dev, y_dev, self.params['max_len'],
                                     self._sentence_lm, self._tag_lm,
                                     batch_size)

                    dev_losses = []
                    pbar = tqdm(pbar, ncols=0)
                    for x_b, y_b, l_b, l_c, ll_c in pbar:
                        x_b = torch.from_numpy(x_b).to(self._get_device())
                        y_b = torch.from_numpy(y_b).to(self._get_device())
                        l_b = torch.from_numpy(l_b).to(self._get_device())
                        if l_c is not None:
                            l_c = torch.from_numpy(l_c).to(self._get_device())
                            ll_c = torch.from_numpy(ll_c).to(
                                self._get_device())
                        loss = model.compute_loss(
                            x_b, y_b, l_b, chars=l_c, charlens=ll_c)
                        dev_losses.append(loss.detach().item())
                    dev_loss = np.mean(dev_losses)
                    if not average_loss:
                        dev_loss /= (predict_batch_size / batch_size)

                if verbose > 0:
                    print('dev loss: {:.4f} dev score table:'.format(dev_loss))
                    print(dev_score)
                if isinstance(save_best, str):
                    if dev_loss < dev_best:
                        print('save best {:.4f} > {:.4f}'.format(
                            dev_best, dev_loss))
                        dev_best = dev_loss
                        dev_best_round = 0
                        save_dir = os.path.realpath(os.path.dirname(save_best))
                        if not os.path.exists(save_dir):
                            os.makedirs(save_dir)
                        with open(save_best, 'wb') as fobj:
                            pickle.dump(self, fobj, protocol=4)
                    else:
                        dev_best_round += 1
                        print('no better {:.4f} <= {:.4f} {}/{}'.format(
                            dev_best, dev_loss, dev_best_round, patient_dev))
                        if isinstance(patient_dev,
                                      int) and dev_best_round >= patient_dev:
                            return
                print()

    def predict(self, X, batch_size=None, verbose=0):
        """Predict tags"""
        model = self._model
        model.eval()
        if batch_size is None:
            batch_size = self.params['batch_size']
        # char_max_len = self.params['char_max_len']
        # Check predictions after training
        data = list(enumerate(X))
        data = sorted(data, key=lambda t: len(t[1]), reverse=True)
        inds = [i for i, _ in data]
        X = [x for _, x in data]
        ret = [None] * len(X)
        with torch.no_grad():
            batch_total = math.ceil(len(X) / batch_size)
            pbar = range(batch_total)
            if verbose > 0:
                pbar = tqdm(pbar, ncols=0)
            for i in pbar:
                ind_batch = inds[i * batch_size:(i + 1) * batch_size]
                x_batch = X[i * batch_size:(i + 1) * batch_size]
                x_batch = [sent[:self.params['max_len']] for sent in x_batch]
                lens = [len(x) for x in x_batch]
                max_len = np.max(lens)

                char_batch = None
                char_len_batch = None
                if self._sentence_lm.use_char:
                    char_batch, char_len_batch = \
                        self._sentence_lm.char_transform(x_batch, max_len)

                    char_batch = torch.from_numpy(np.asarray(char_batch)).to(
                        self._get_device())
                    char_len_batch = torch.from_numpy(
                        np.asarray(char_len_batch,
                                   dtype=np.int32)).to(self._get_device())

                x_batch = self._sentence_lm.transform(x_batch, max_len)
                sent = torch.from_numpy(np.asarray(x_batch)).to(
                    self._get_device())
                lens = torch.Tensor(lens).long().to(self._get_device())
                _, predicts = model(sent, lens, char_batch, char_len_batch)

                for ind, tag_len, tags in zip(ind_batch, lens, predicts):
                    # tags = [ix_to_tag[i] for i in tags[:tag_len]]
                    tags = self._tag_lm.inverse_transform([tags])[0]
                    ret[ind] = tags
        return ret

    def _get_sets(self, X, y, verbose, batch_size):
        preds = self.predict(X, verbose=verbose, batch_size=batch_size)
        pbar = enumerate(zip(preds, y))
        if verbose > 0:
            pbar = tqdm(pbar, ncols=0, total=len(y))

        apset = []
        arset = []
        for i, (pred, y_true) in pbar:
            pset = extract_entities(pred)
            rset = extract_entities(y_true)
            for item in pset:
                apset.append(tuple([i] + list(item)))
            for item in rset:
                arset.append(tuple([i] + list(item)))
        return apset, arset

    def score(self, X, y, batch_size=None, verbose=0, detail=False):
        """Calculate NER F1
        Based CONLL 2003 standard
        """
        apset, arset = self._get_sets(X, y, verbose, batch_size)
        pset = set(apset)
        rset = set(arset)
        inter = pset.intersection(rset)
        precision = len(inter) / len(pset) if pset else 1
        recall = len(inter) / len(rset) if rset else 1
        f1score = 0
        if precision + recall > 0:
            f1score = 2 * ((precision * recall) / (precision + recall))
        if detail:
            return precision, recall, f1score
        return f1score

    def score_table(self, X, y, batch_size=None, verbose=0):
        """Calculate NER F1
        Based CONLL 2003 standard
        """
        apset, arset = self._get_sets(X, y, verbose, batch_size)
        types = [x[3] for x in apset] + [x[3] for x in arset]
        types = sorted(set(types))
        rows = []
        for etype in types:
            pset = set([x for x in apset if x[3] == etype])
            rset = set([x for x in arset if x[3] == etype])
            inter = pset.intersection(rset)
            precision = len(inter) / len(pset) if pset else 1
            recall = len(inter) / len(rset) if rset else 1
            f1score = 0
            if precision + recall > 0:
                f1score = 2 * ((precision * recall) / (precision + recall))
            rows.append((etype, precision, recall, f1score))
        pset = set(apset)
        rset = set(arset)
        inter = pset.intersection(rset)
        precision = len(inter) / len(pset) if pset else 1
        recall = len(inter) / len(rset) if rset else 1
        f1score = 0
        if precision + recall > 0:
            f1score = 2 * ((precision * recall) / (precision + recall))
        rows.append(('TOTAL', precision, recall, f1score))
        df = pd.DataFrame(
            rows, columns=['name', 'precision', 'recall', 'f1score'])
        df.index = df['name']
        df = df.drop('name', axis=1)
        return df

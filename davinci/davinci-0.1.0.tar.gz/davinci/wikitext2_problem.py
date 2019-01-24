#!/usr/bin/env python

"""
This example is largely inspired from the PyTorch example available at:
https://github.com/pytorch/examples/
"""

import os
import urllib
from math import ceil

import torch as th
import torch.nn as nn
import torch.nn.functional as F
import torch.optim as optim
from torchvision import datasets, transforms
from torch.autograd import Variable

from os.path import expanduser


class BatchedDataset(object):
    def __init__(self, data, bptt, cuda=True):
        self.dataset = data
        if cuda:
            self.dataset = self.dataset.cuda()
        self.bptt = bptt

    def __len__(self):
        return ceil((self.dataset.size(0) - 1) / self.bptt)

    def __getitem__(self, index):
        return self.get_batch(self.dataset, index)

    def __iter__(self):
        for i in range(len(self)):
            yield self.__getitem__(i)

    def get_batch(self, source, i, evaluation=False):
        i = i * self.bptt
        seq_len = min(self.bptt, len(source) - 1 - i)
        data = source[i:i+seq_len]
        target = source[i+1:i+1+seq_len].view(-1)
        return data, target


class Dictionary(object):

    def __init__(self):
        self.word2idx = {}
        self.idx2word = []

    def add_word(self, word):
        if word not in self.word2idx:
            self.idx2word.append(word)
            self.word2idx[word] = len(self.idx2word) - 1
        return self.word2idx[word]

    def __len__(self):
        return len(self.idx2word)


class Corpus(object):

    def __init__(self, path):
        path = os.path.join(path, 'wikitext2')
        if not os.path.exists(path):
            self._download_dataset(path)
        self.dictionary = Dictionary()
        self.train = self.tokenize(os.path.join(path, 'train.txt'))
        self.valid = self.tokenize(os.path.join(path, 'valid.txt'))
        self.test = self.tokenize(os.path.join(path, 'test.txt'))

    def tokenize(self, path):
        """Tokenizes a text file."""
        assert os.path.exists(path)
        # Add words to the dictionary
        with open(path, 'r') as f:
            tokens = 0
            for line in f:
                words = line.split() + ['<eos>']
                tokens += len(words)
                for word in words:
                    self.dictionary.add_word(word)

        # Tokenize file content
        with open(path, 'r') as f:
            ids = th.LongTensor(tokens)
            token = 0
            for line in f:
                words = line.split() + ['<eos>']
                for word in words:
                    ids[token] = self.dictionary.word2idx[word]
                    token += 1
        return ids
    
    def _download_dataset(self, path='./'):
        path = os.path.abspath(path)
        print('downloading data to: ', path)
        os.makedirs(path)
        train_url = 'https://cdn.jsdelivr.net/gh/pytorch/examples@dcdabc22b305d2f2989c6f03570dfcd3919e8a5b/word_language_model/data/wikitext-2/train.txt'
        valid_url = 'https://cdn.jsdelivr.net/gh/pytorch/examples@dcdabc22b305d2f2989c6f03570dfcd3919e8a5b/word_language_model/data/wikitext-2/valid.txt'
        test_url = 'https://cdn.jsdelivr.net/gh/pytorch/examples@dcdabc22b305d2f2989c6f03570dfcd3919e8a5b/word_language_model/data/wikitext-2/test.txt'
        train_file = os.path.join(path, 'train.txt')
        valid_file = os.path.join(path, 'valid.txt')
        test_file = os.path.join(path, 'test.txt')
        urllib.request.urlretrieve(train_url, train_file)
        urllib.request.urlretrieve(valid_url, valid_file)
        urllib.request.urlretrieve(test_url, test_file)


def batchify(data, bsz):
    # Work out how cleanly we can divide the dataset into bsz parts.
    nbatch = data.size(0) // bsz
    # Trim off any extra elements that wouldn't cleanly fit (remainders).
    data = data.narrow(0, 0, nbatch * bsz)
    # Evenly divide the data across the bsz batches.
    data = data.view(bsz, -1).t().contiguous()
    return data


def repackage_hidden(h):
    """Wraps hidden states in new Variables, to detach them from their history."""
    if type(h) == Variable:
        return Variable(h.data, requires_grad=False)
    else:
        return tuple(repackage_hidden(v) for v in h)


class RNNModel(nn.Module):
    """Container module with an encoder, a recurrent module, and a decoder."""

    def __init__(self, cell, ntokens, ninp, nhid, nlayers, bsz=16, dropout=0.2,
                 tie_weights=True):
        super(RNNModel, self).__init__()
        self.is_rnn = True
        self.drop = nn.Dropout(dropout)
        self.encoder = nn.Embedding(ntokens, ninp)
        self.rnn = cell(ninp, nhid, nlayers, dropout)
        self.decoder = nn.Linear(nhid, ntokens)

        # Optionally tie weights as in:
        # "Using the Output Embedding to Improve Language Models" (Press & Wolf 2016)
        # https://arxiv.org/abs/1608.05859
        # and
        # "Tying Word Vectors and Word Classifiers: A Loss Framework for Language Modeling" (Inan et al. 2016)
        # https://arxiv.org/abs/1611.01462
        if tie_weights:
            if nhid != ninp:
                raise ValueError(
                    'When using the tied flag, nhid must be equal to emsize')
            self.decoder.weight = self.encoder.weight

        self.init_weights()

        self.cell = cell
        self.nhid = nhid
        self.nlayers = nlayers
        self.ntokens = ntokens
        self.bsz = bsz

    def init_weights(self):
        initrange = 0.1
        self.encoder.weight.data.uniform_(-initrange, initrange)
        self.decoder.bias.data.fill_(0)
        self.decoder.weight.data.uniform_(-initrange, initrange)

    def repackage_hidden(self):
        self.hidden = repackage_hidden(self.hidden)

    def forward(self, input):
        self.rnn.flatten_parameters()
        self.hidden = repackage_hidden(self.hidden)
        hidden = self.hidden
        emb = self.drop(self.encoder(input))
        output, hidden = self.rnn(emb, hidden)
        output = self.drop(output)
        decoded = self.decoder(output.view(
            output.size(0) * output.size(1), output.size(2)))
        self.hidden = hidden
        # return decoded.view(output.size(0), output.size(1), decoded.size(1))
        out = decoded.view(output.size(0), output.size(1), decoded.size(1))
        return out.view(-1, self.ntokens)

    def init_hidden(self, bsz):
        weight = next(self.parameters()).data
        if self.cell == nn.LSTM:
            self.hidden = (Variable(weight.new(self.nlayers, bsz, self.nhid).zero_()),
                    Variable(weight.new(self.nlayers, bsz, self.nhid).zero_()))
        else:
            self.hidden = Variable(weight.new(self.nlayers, bsz, self.nhid).zero_())

    def train(self, *args, **kwargs):
        super(RNNModel, self).train(*args, **kwargs)
        self.init_hidden(self.bsz)

    def eval(self, *args, **kwargs):
        super(RNNModel, self).eval(*args, **kwargs)
        self.init_hidden(self.bsz)


def grad_norm_then_opt(step, model, clip=0.25):
    def norm_then_opt():
        th.nn.utils.clip_grad_norm(model.parameters(), clip)
        step()
    return norm_then_opt


class LRAnnealer(object):

    def __init__(self, opt, factor=4.0):
        self.opt = opt
        self.factor = factor
        self.best_value = float('inf')

    def step(self, value):
        if value < self.best_value:
            self.best_value = value
        else:
            for g in self.opt.param_groups:
                g['lr'] = g['lr'] / self.factor


def get_wikitext2(
        batch_size=20,
        lr=20.0,
        momentum=0.0,
        cuda=False,
        data_path=expanduser('~/.davinci/data/'),
        model=None,
        valid=False,
        ):

    # TODO: Try dataloader to see if training is faster. (Might be)

    bsz = batch_size
    # Load data
    corpus = Corpus(data_path)
    eval_bsz = bsz
    bptt = 35
    train_data = batchify(corpus.train, bsz)
    test_data = batchify(corpus.test, eval_bsz)
    train_data = BatchedDataset(train_data, bptt, cuda=cuda)
    test_data = BatchedDataset(test_data, bptt, cuda=cuda)
    ntokens = len(corpus.dictionary)

    # Build model
    if model is None:
        cell = nn.LSTM
        model = RNNModel(cell, ntokens, ninp=200, nhid=200, nlayers=2, bsz=bsz, dropout=0.2, tie_weights=True)
    #    model = RNNModel(cell, ntokens, ninp=650, nhid=650, nlayers=2, bsz=bsz, dropout=0.5, tie_weights=True)
    
    if cuda:
        model = model.cuda()

    loss = nn.CrossEntropyLoss()

    opt = optim.SGD(model.parameters(), lr=lr, momentum=momentum)
    opt.step = grad_norm_then_opt(opt.step, model, clip=0.25)
    scheduler = LRAnnealer(opt, 4.0)
    num_epochs = 40
    if valid:
        valid_data = batchify(corpus.valid, eval_bsz)
        valid_data = BatchedDataset(valid_data, bptt, cuda=cuda)
        return model, (train_data, valid_data, test_data), loss, opt, scheduler, num_epochs
    return model, (train_data, test_data), loss, opt, scheduler, num_epochs

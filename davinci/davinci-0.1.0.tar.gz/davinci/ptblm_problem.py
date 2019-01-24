#!/usr/bin/env python

"""
This example is largely inspired from the PyTorch example available at:
https://github.com/pytorch/examples/
"""

import os
from math import ceil

import torch as th
import torch.nn as nn
import torch.nn.functional as F
from torchvision import datasets, transforms
from torch.autograd import Variable

from .loss import L1, L2
from .datasets import DataPartitioner
from .utils import FuncNet, get_optimizer, get_dist, get_cell


class BatchedDataset(object):
    def __init__(self, data, bptt):
        self.data = data
        self.bptt = bptt

    def __len__(self):
        return ceil((self.data.size(0) - 1) / self.bptt) 

    def __getitem__(self, index):
        return self.get_batch(self.data, index)

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


def batchify(data, bsz, cuda):
    # Work out how cleanly we can divide the dataset into bsz parts.
    nbatch = data.size(0) // bsz
    # Trim off any extra elements that wouldn't cleanly fit (remainders).
    data = data.narrow(0, 0, nbatch * bsz)
    # Evenly divide the data across the bsz batches.
    data = data.view(bsz, -1).t().contiguous()
    if cuda:
        data = data.cuda()
    return data


def repackage_hidden(h):
    """Wraps hidden states in new Variables, to detach them from their history."""
    if type(h) == Variable:
        return Variable(h.data)
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

    def forward(self, input):
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


def get_ptblm(args):
    # TODO: Use the right hyper-params, they are weird. And gradient clipping.
    rank = args.rank
    size = args.size
    cuda = args.cuda

    # Load data
    corpus = Corpus('data/penn')
    bsz = args.bsz // size
    eval_bsz = bsz
    bptt = 35
    train_data = batchify(corpus.train, bsz, cuda)
    test_data = batchify(corpus.test, eval_bsz, cuda)
    train_data = BatchedDataset(train_data, bptt)
    test_data = BatchedDataset(test_data, bptt)
    ntokens = len(corpus.dictionary)


    partition_sizes = [1.0 / size for _ in range(size)]
    train_data = DataPartitioner(train_data, partition_sizes).use(rank)
    test_data = DataPartitioner(test_data, partition_sizes).use(rank)

    # Build model
    cell = get_cell(args)
    #Smaller: model = RNNModel(cell, ntokens, ninp=200, nhid=200, nlayers=2, bsz=bsz, dropout=0.2, tie_weights=True)
    model = RNNModel(cell, ntokens, ninp=650, nhid=650, nlayers=2, bsz=bsz, dropout=0.5, tie_weights=True)

    if size == 1:
        model = nn.DataParallel(model, device_ids=[0, 2])

    if cuda:
        model.cuda()

    loss = nn.CrossEntropyLoss()
    if args.regL == 1:
        loss = L1(loss, model.parameters(), lam=args.lam)
    elif args.regL == 2:
        loss = L2(loss, model.parameters(), lam=args.lam)

    opt = get_optimizer(args, model.parameters())
    opt = get_dist(args, opt)
    num_epochs = args.epochs
    return model, (train_data, test_data), loss, opt, num_epochs

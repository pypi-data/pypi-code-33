#!/usr/bin/env python

"""
This example is largely inspired from the PyTorch example available at:
https://github.com/pytorch/examples/
"""

import os
import torch
import torch as th
import torch.nn as nn
import torch.nn.functional as F

from torch.autograd import Variable

from torchtext import data, datasets

from .loss import L1, L2
from .datasets import DataPartitioner
from .utils import FuncNet, get_optimizer, get_dist


def makedirs(name):
    """helper function for python 2 and 3 to call os.makedirs()
       avoiding an error if the directory to be created already exists"""

    import os, errno

    try:
        os.makedirs(name)
    except OSError as ex:
        if ex.errno == errno.EEXIST and os.path.isdir(name):
            # ignore existing directory
            pass
        else:
            # a different error happened
            raise

class Bottle(nn.Module):

    def forward(self, input):
        if len(input.size()) <= 2:
            return super(Bottle, self).forward(input)
        size = input.size()[:2]
        out = super(Bottle, self).forward(input.view(size[0]*size[1], -1))
        return out.view(size[0], size[1], -1)


class Linear(Bottle, nn.Linear):
    pass


class Encoder(nn.Module):

    def __init__(self, config):
        super(Encoder, self).__init__()
        self.config = config
        input_size = config.d_proj if config.projection else config.d_embed
        self.rnn = nn.LSTM(input_size=input_size, hidden_size=config.d_hidden,
                        num_layers=config.n_layers, dropout=config.dp_ratio,
                        bidirectional=config.birnn)

    def forward(self, inputs):
        batch_size = inputs.size()[1]
        state_shape = self.config.n_cells, batch_size, self.config.d_hidden
        h0 = c0 = Variable(inputs.data.new(*state_shape).zero_())
        self.rnn.flatten_parameters()
        outputs, (ht, ct) = self.rnn(inputs, (h0, c0))
        return ht[-1] if not self.config.birnn else ht[-2:].transpose(0, 1).contiguous().view(batch_size, -1)


class SNLIClassifier(nn.Module):

    def __init__(self, config):
        super(SNLIClassifier, self).__init__()
        self.config = config
        self.embed = nn.Embedding(config.n_embed, config.d_embed)
        self.projection = Linear(config.d_embed, config.d_proj)
        self.encoder = Encoder(config)
        self.dropout = nn.Dropout(p=config.dp_ratio)
        self.relu = nn.ReLU()
        seq_in_size = 2*config.d_hidden
        if self.config.birnn:
            seq_in_size *= 2
        lin_config = [seq_in_size]*2
        self.out = nn.Sequential(
            Linear(*lin_config),
            self.relu,
            self.dropout,
            Linear(*lin_config),
            self.relu,
            self.dropout,
            Linear(*lin_config),
            self.relu,
            self.dropout,
            Linear(seq_in_size, config.d_out))

    def forward(self, batch):
        prem_embed = self.embed(batch.premise)
        hypo_embed = self.embed(batch.hypothesis)
        if self.config.fix_emb:
            prem_embed = Variable(prem_embed.data)
            hypo_embed = Variable(hypo_embed.data)
        if self.config.projection:
            prem_embed = self.relu(self.projection(prem_embed))
            hypo_embed = self.relu(self.projection(hypo_embed))
        premise = self.encoder(prem_embed)
        hypothesis = self.encoder(hypo_embed)
        scores = self.out(torch.cat([premise, hypothesis], 1))
        return scores

class Conf(object):
    pass

class CustomBatchIterator(object):

    def __init__(self, batch):
        self.batch = batch
        self.iter_batch = iter(batch)

    def __iter__(self):
        return self

    def init_epoch(self):
        self.batch.init_epoch()
        self.iter_batch = iter(self.batch)

    def __len__(self):
        return len(self.batch)

    def __next__(self):
        b = next(self.iter_batch)
        return(b, b.label)


def get_snli(args):
    rank = args.rank
    size = args.size
    cuda = args.cuda

    
    # Dataloading and Dataset creation
    inputs = data.Field(lower=True)
    answers = data.Field(sequential=False)
    train, dev, test = datasets.SNLI.splits(inputs, answers)
    inputs.build_vocab(train, dev, test)
    vector_cache = os.path.join(os.getcwd(), '.vector_cache/input_vectors.pt')
    if os.path.isfile(vector_cache):
        inputs.vocab.vectors = torch.load(vector_cache)
    else:
        inputs.vocab.load_vectors(wv_dir=os.path.join(os.getcwd(), '.data_cache'),
                                  wv_type='glove.42B', wv_dim=300)
        makedirs(os.path.dirname(vector_cache))
        torch.save(inputs.vocab.vectors, vector_cache)

    answers.build_vocab(train)

    partition_sizes = [1.0 / size for _ in range(size)]
    part = DataPartitioner(train, partition_sizes).use(rank)
    part.sort_key = train.sort_key
    part.fields = train.fields
    train = part
    train_iter, dev_iter, test_iter = data.BucketIterator.splits(
        (train, dev, test), batch_size=128, device=th.cuda.current_device())
    train_iter.repeat = False
    train_iter = CustomBatchIterator(train_iter)
    test_iter = CustomBatchIterator(test_iter)

    # Model creation
    conf = Conf()
    conf.n_embed = len(inputs.vocab)
    conf.d_embed = 300
    conf.d_proj = 300
    conf.dp_ratio = 0.2
    conf.d_hidden = 300
    conf.birnn = True
    conf.d_out = len(answers.vocab)
    conf.projection = True
    conf.d_hidden = 300
    conf.n_layers = 1
    conf.n_cells = conf.n_layers
    conf.fix_emb = True
    if conf.birnn:
        conf.n_cells *= 2
    model = SNLIClassifier(conf)
    model.embed.weight.data = inputs.vocab.vectors
    model.cuda()

    # Loss
    loss = nn.CrossEntropyLoss()
    opt = get_optimizer(args, model.parameters())
    opt = get_dist(args, opt)
    num_epochs = args.epochs

    return model, (train_iter, test_iter), loss, opt, num_epochs

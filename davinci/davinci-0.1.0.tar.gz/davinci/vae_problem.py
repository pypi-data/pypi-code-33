#!/usr/bin/env python
"""
This example is largely inspired from the PyTorch example available at:
https://github.com/pytorch/examples/
"""

import torch as th
import torch.nn as nn
import torch.nn.functional as F
from torch.autograd import Variable as V
from torchvision import datasets, transforms

from .loss import L1, L2
from .datasets import DataPartitioner
from .utils import FuncNet, get_optimizer, get_dist


class Swish(nn.Module):
    def forward(self, x):
        return x * F.sigmoid(x)


class VAE(nn.Module):
    def __init__(self):
        super(VAE, self).__init__()

        self.fc1 = nn.Linear(784, 400)
        self.fc21 = nn.Linear(400, 20)
        self.fc22 = nn.Linear(400, 20)
        self.fc3 = nn.Linear(20, 400)
        self.fc4 = nn.Linear(400, 784)

        self.relu = nn.ReLU()
#        self.relu = nn.Sigmoid()
#        self.relu = Swish()
        self.sigmoid = nn.Sigmoid()

    def encode(self, x):
        h1 = self.relu(self.fc1(x))
        return self.fc21(h1), self.fc22(h1)

    def reparameterize(self, mu, logvar):
        if self.training:
            std = logvar.mul(0.5).exp_()
            eps = V(std.data.new(std.size()).normal_())
            return eps.mul(std).add_(mu)
        else:
            return mu

    def decode(self, z):
        h3 = self.relu(self.fc3(z))
        return self.sigmoid(self.fc4(h3))

    def forward(self, x):
        mu, logvar = self.encode(x.view(-1, 784))
        z = self.reparameterize(mu, logvar)
        return self.decode(z), mu, logvar


class DoubleInputIterator(object):

    def __init__(self, dataset):
        self.dataset = dataset

    def __len__(self):
        return len(self.dataset)

    def __iter__(self):
        for X, y in self.dataset:
            yield X, X


def get_vae(args):
    rank = args.rank
    size = args.size
    cuda = args.cuda

    model = VAE()

    if cuda:
        model.cuda()
        kwargs = {'num_workers': 1, 'pin_memory': True}
    else:
        kwargs = {}

    bsz = args.bsz // size

    dataset = datasets.MNIST(
        './data',
        train=True,
        download=True,
        transform=transforms.Compose([
            transforms.ToTensor(),
        ]))
    partition_sizes = [1.0 / size for _ in range(size)]
    partition = DataPartitioner(dataset, partition_sizes).use(rank)
    train_set = th.utils.data.DataLoader(
        partition, batch_size=bsz, shuffle=True, **kwargs)

    test_set = th.utils.data.DataLoader(
        datasets.MNIST(
            './data',
            train=False,
            transform=transforms.Compose([
                transforms.ToTensor(),
            ])),
        batch_size=bsz,
        shuffle=True,
        **kwargs)
    train_set = DoubleInputIterator(train_set)
    test_set = DoubleInputIterator(test_set)

    def vae_loss(label, target):
        x = target
        recon_x, mu, logvar = label
        BCE = F.binary_cross_entropy(recon_x, x.view(-1, 784))
        # see Appendix B from VAE paper:
        # Kingma and Welling. Auto-Encoding Variational Bayes. ICLR, 2014
        # https://arxiv.org/abs/1312.6114
        # 0.5 * sum(1 + log(sigma^2) - mu^2 - sigma^2)
        KLD = -0.5 * th.sum(1.0 + logvar - mu.pow(2) - logvar.exp())
        # Normalise by same number of elements as in reconstruction
        KLD /= bsz * 784.0
        return BCE + KLD

    opt = get_optimizer(args, model.parameters())
    opt = get_dist(args, opt)
    num_epochs = args.epochs

    return model, (train_set, test_set), vae_loss, opt, num_epochs

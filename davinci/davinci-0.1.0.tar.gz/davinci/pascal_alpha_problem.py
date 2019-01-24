#!/usr/bin/env python3

import os
import urllib

from bz2 import BZ2File

import torch.nn as nn
import torch.optim as optim
from torch import Tensor as T
import torch.nn.functional as F
from torch.utils.data import Dataset, DataLoader

from os.path import expanduser

from .mnist_problem import NoOptScheduler
from .utils import split_dataset


class AlphaDataset(Dataset):
    def __init__(self, data_path='data/', train=True, cuda=False):
        data_path = os.path.join(data_path, 'pascal')
        data_path = os.path.join(data_path, 'alpha')
        if not os.path.exists(data_path):
            self._download_data(data_path)
        features_path = os.path.join(data_path, 'alpha_train.dat')
        labels_path = os.path.join(data_path, 'alpha_train.lab')
        fd_features = open(features_path, 'r')
        fd_labels = open(labels_path, 'r')
        self.features = []
        self.labels = []
        for i, (X, y) in enumerate(zip(fd_features, fd_labels)):
            if (i >= 400000 and train) or (i < 400000 and not train):
                continue
            y = 1 if y == 1 else 0
            X = [float(x) for x in X.strip().split(' ')]
            self.features.append(X)
            self.labels.append(y)
        X = T(self.features)
        mu = X.mean(dim=0)
        sigma = X.std(dim=0)
        self.features = ((X - mu) / sigma).float()
        self.labels = T(self.labels).long()
        if cuda:
            self.features = self.features.cuda()
            self.labels = self.labels.cuda()

    def __len__(self):
        return len(self.features)

    def __getitem__(self, idx):
        X = self.features[idx]
        y = self.labels[idx]
        return X, y

    def _download_data(self, path):
        path = os.path.abspath(path)
        print('downloading data to: ', path)
        os.makedirs(path)
        data_url = 'ftp://largescale.ml.tu-berlin.de/largescale/alpha/alpha_train.dat.bz2'
        labels_url = 'ftp://largescale.ml.tu-berlin.de/largescale/alpha/alpha_train.lab.bz2'
        data_file = os.path.join(path, 'alpha_train.dat.bz2')
        labels_file = os.path.join(path, 'alpha_train.lab.bz2')
        urllib.request.urlretrieve(data_url, data_file)
        urllib.request.urlretrieve(labels_url, labels_file)
        self._unbzip2(data_file)
        self._unbzip2(labels_file)

    def _unbzip2(self, file_path):
        new_path = file_path[:-4]
        with open(new_path, 'wb') as new_file, BZ2File(file_path) as f:
            for data in iter(lambda: f.read(100 * 1024), b''):
                new_file.write(data)


class LogisticRegression(nn.Module):

    def __init__(self, in_size=10, out_size=2):
        super(LogisticRegression, self).__init__()
        self.fc = nn.Linear(in_size, out_size)

    def forward(self, x):
        x = self.fc(x)
        x = F.log_softmax(x)
        return x


def get_pascal_alpha(
        batch_size=1,
        lr=0.1,
        momentum=0.0,
        cuda=False,
        data_path=expanduser('~/.davinci/data/'),
        model=None,
        valid=False,
        ):
    num_epochs = 50
    train_data = AlphaDataset(data_path, train=True)
    train_set = DataLoader(train_data,
                           batch_size=batch_size,
                           shuffle=True,
                           pin_memory=cuda,
                           num_workers=2)
    test_data = AlphaDataset(data_path, train=False)
    test_set = DataLoader(test_data,
                          batch_size=batch_size,
                          shuffle=True,
                          pin_memory=cuda,
                          num_workers=2)
    if model is None:
        model = LogisticRegression(500, 2)
    if cuda:
        model = model.cuda()
    loss = F.nll_loss
    opt = optim.SGD(model.parameters(),
                    lr=lr,
                    momentum=momentum,
                    weight_decay=0.01)
    scheduler = NoOptScheduler()

    if valid:
        num_valid = 60000
        num_train = len(train_data) - num_valid
        train_data, valid_data = split_dataset(train_data,
                                               [num_train, num_valid])
        train_set = DataLoader(train_data, batch_size=batch_size,
                               shuffle=True)
        valid_set = DataLoader(valid_data, batch_size=batch_size,
                               shuffle=False)
        return model, (train_set, valid_set, test_set), loss, opt, scheduler, num_epochs

    return model, (train_set, test_set), loss, opt, scheduler, num_epochs

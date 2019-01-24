#!/usr/bin/env python3

import os
import requests
import tarfile

import torch.nn as nn
import torch.optim as optim
from torch import Tensor as T
import torch.nn.functional as F
from torch.utils.data import Dataset, DataLoader

from os.path import expanduser

from .mnist_problem import NoOptScheduler
from .utils import split_dataset


def download_file(url, dest):
    """
    https://stackoverflow.com/questions/16694907/how-to-download-large-file-in-python-with-requests-py
    """
    r = requests.post(url, stream=True, data={'username': 'seba-1511', 'password': 'pass90861'})
    with open(dest, 'wb') as f:
        for chunk in r.iter_content(chunk_size=1024):
            if chunk:  # filter out keep-alive new chunks
                f.write(chunk)


class ProteinDataset(Dataset):
    def __init__(self, data_path='data/', train=True, cuda=False):
        data_path = os.path.join(data_path, 'kdd')
        data_path = os.path.join(data_path, 'protein')
        if not os.path.exists(data_path):
            self._download_data(data_path)

        features_path = os.path.join(data_path, 'bio_train.dat')

        fd_features = open(features_path, 'r')
        features = fd_features.readlines()
        self.features = []
        for i, X in enumerate(features):
            if (i >= 100000 and train) or (i < 100000 and not train):
                continue
            X = [float(x) for x in X.strip().split('\t')]
            self.features.append(X)
        X = T(self.features)
        Y = X[:, 2]
        X = X[:, 3:]
        mu = X.mean(dim=0)
        sigma = X.std(dim=0)
        self.features = ((X - mu) / sigma).float()
        self.labels = Y.long()
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
        data_url = 'http://osmot.cs.cornell.edu/cgi-bin/kddcup/data_kddcup04.tar.gz'
        data_file = os.path.join(path, 'data_kddcup04.tar.gz')
        download_file(data_url, data_file)
        self._deflate(data_file, path)

    def _deflate(self, file_path, extract_path):
        if file_path.endswith("tar.gz"):
            tar = tarfile.open(file_path, "r:gz")
            tar.extractall(path=extract_path)
            tar.close()
        elif file_path.endswith("tar"):
            tar = tarfile.open(file_path, "r:")
            tar.extractall(path=extract_path)
            tar.close()


class LogisticRegression(nn.Module):

    def __init__(self, in_size=10, out_size=2):
        super(LogisticRegression, self).__init__()
        self.fc = nn.Linear(in_size, out_size)

    def forward(self, x):
        x = self.fc(x)
        x = F.log_softmax(x)
        return x


def get_kdd_protein(
        batch_size=1,
        lr=0.1,
        momentum=0.0,
        cuda=False,
        data_path=expanduser('~/.davinci/data/'),
        model=None,
        valid=False,
        ):
    num_epochs = 50
    train_data = ProteinDataset(data_path, train=True)
    train_set = DataLoader(train_data,
                           batch_size=batch_size,
                           shuffle=True,
                           pin_memory=cuda,
                           num_workers=2)
    test_data = ProteinDataset(data_path, train=False)
    test_set = DataLoader(test_data,
                          batch_size=batch_size,
                          shuffle=True,
                          pin_memory=cuda,
                          num_workers=2)
    if model is None:
        model = LogisticRegression(74, 2)
    if cuda:
        model = model.cuda()
    loss = F.nll_loss
    opt = optim.SGD(model.parameters(),
                    lr=lr,
                    momentum=momentum,
                    weight_decay=0.01)
    scheduler = NoOptScheduler()

    if valid:
        num_valid = 30000
        num_train = len(train_data) - num_valid
        train_data, valid_data = split_dataset(train_data,
                                               [num_train, num_valid])
        train_set = DataLoader(train_data, batch_size=batch_size,
                               shuffle=True)
        valid_set = DataLoader(valid_data, batch_size=batch_size,
                               shuffle=False)
        return model, (train_set, valid_set, test_set), loss, opt, scheduler, num_epochs

    return model, (train_data, test_data), loss, opt, scheduler, num_epochs

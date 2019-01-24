#!/usr/bin/env python

"""
This example is largely inspired from the PyTorch example available at:
https://github.com/pytorch/examples/
"""

import torch.nn as nn
import torch.nn.functional as F
import torch.optim as optim

from torch.utils.data import DataLoader
from torchvision import datasets, transforms

from os.path import expanduser

from .utils import NoOptScheduler, split_dataset


class MNISTNet(nn.Module):
    def __init__(self):
        super(MNISTNet, self).__init__()
        self.conv1 = nn.Conv2d(1, 10, kernel_size=5)
        self.conv2 = nn.Conv2d(10, 20, kernel_size=5)
        self.conv2_drop = nn.Dropout2d()
        self.fc1 = nn.Linear(320, 50)
        self.fc2 = nn.Linear(50, 10)

    def forward(self, x):
        x = F.relu(F.max_pool2d(self.conv1(x), 2))
        x = self.conv2(x)
        x = self.conv2_drop(x)
        x = F.relu(F.max_pool2d(x, 2))
        x = x.view(-1, 320)
        x = F.relu(self.fc1(x))
        x = F.dropout(x, training=self.training)
        x = self.fc2(x)
        return F.log_softmax(x, dim=1)


def get_mnist(
        batch_size=64,
        lr=0.01,
        momentum=0.5,
        cuda=False,
        data_path=expanduser('~/.davinci/data'),
        model=None,
        valid=False,
        ):

    if model is None:
        model = MNISTNet()

    kwargs = {'num_workers': 1, 'pin_memory': True}
    if cuda:
        model = model.cuda()

    bsz = batch_size

    dataset = datasets.MNIST(data_path,
                             train=True,
                             download=True,
                             transform=transforms.Compose([
                                 transforms.ToTensor(),
                                 transforms.Normalize((0.1307,), (0.3081,)),
                             ]))
    train_set = DataLoader(dataset, batch_size=bsz, shuffle=True, **kwargs)

    test_set = DataLoader(
        datasets.MNIST(data_path,
                       train=False,
                       transform=transforms.Compose([
                            transforms.ToTensor(),
                            transforms.Normalize((0.1307,), (0.3081,)),
        ])),
        batch_size=bsz, shuffle=False, **kwargs)

    loss = F.nll_loss

    num_epochs = 10
    opt = optim.SGD(model.parameters(), lr=lr, momentum=momentum)
    scheduler = NoOptScheduler()

    if valid:
        num_valid = len(test_set.dataset)
        num_train = len(dataset) - num_valid
        train_data, valid_data = split_dataset(dataset,
                                               [num_train, num_valid])
        train_set = DataLoader(train_data, batch_size=bsz,
                               shuffle=True, **kwargs)
        valid_set = DataLoader(valid_data, batch_size=bsz,
                               shuffle=False, **kwargs)
        return model, (train_set, valid_set, test_set), loss, opt, scheduler, num_epochs

    return model, (train_set, test_set), loss, opt, scheduler, num_epochs

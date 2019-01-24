#!/usr/bin/env python

"""
This example is largely inspired from the PyTorch implementation available at:
https://github.com/kuangliu/pytorch-cifar
"""

import math
import torch
import torch.nn as nn
import torch.optim as optim
import torch.nn.functional as F
from torch.utils.data import DataLoader
from torchvision import datasets, transforms

from os.path import expanduser

from .utils import split_dataset


class CNN(nn.Module):

    def __init__(self):

        super(CNN, self).__init__()
        self.conv1 = nn.Conv2d(3, 6, 5)
        self.pool = nn.MaxPool2d(2, 2)
        self.conv2 = nn.Conv2d(6, 16, 5)
        self.fc1 = nn.Linear(16 * 5 * 5, 120)
        self.fc2 = nn.Linear(120, 84)
        self.fc3 = nn.Linear(84, 10)

    def forward(self, x):
        x = self.pool(F.relu(self.conv1(x)))
        x = self.pool(F.relu(self.conv2(x)))
        x = x.view(-1, 16 * 5 * 5)
        x = F.relu(self.fc1(x))
        x = F.relu(self.fc2(x))
        x = self.fc3(x)
        return x

class Bottleneck(nn.Module):
    def __init__(self, in_planes, growth_rate):
        super(Bottleneck, self).__init__()
        self.bn1 = nn.BatchNorm2d(in_planes)
        self.conv1 = nn.Conv2d(in_planes, 4*growth_rate, kernel_size=1, bias=False)
        self.bn2 = nn.BatchNorm2d(4*growth_rate)
        self.conv2 = nn.Conv2d(4*growth_rate, growth_rate, kernel_size=3, padding=1, bias=False)

    def forward(self, x):
        out = self.conv1(F.relu(self.bn1(x)))
        out = self.conv2(F.relu(self.bn2(out)))
        out = torch.cat([out,x], 1)
        return out


class Transition(nn.Module):
    def __init__(self, in_planes, out_planes):
        super(Transition, self).__init__()
        self.bn = nn.BatchNorm2d(in_planes)
        self.conv = nn.Conv2d(in_planes, out_planes, kernel_size=1, bias=False)

    def forward(self, x):
        out = self.conv(F.relu(self.bn(x)))
        out = F.avg_pool2d(out, 2)
        return out


class DenseNet(nn.Module):
    def __init__(self, block, nblocks, growth_rate=12, reduction=0.5, num_classes=10):
        super(DenseNet, self).__init__()
        self.growth_rate = growth_rate

        num_planes = 2*growth_rate
        self.conv1 = nn.Conv2d(3, num_planes, kernel_size=3, padding=1, bias=False)

        self.dense1 = self._make_dense_layers(block, num_planes, nblocks[0])
        num_planes += nblocks[0]*growth_rate
        out_planes = int(math.floor(num_planes*reduction))
        self.trans1 = Transition(num_planes, out_planes)
        num_planes = out_planes

        self.dense2 = self._make_dense_layers(block, num_planes, nblocks[1])
        num_planes += nblocks[1]*growth_rate
        out_planes = int(math.floor(num_planes*reduction))
        self.trans2 = Transition(num_planes, out_planes)
        num_planes = out_planes

        self.dense3 = self._make_dense_layers(block, num_planes, nblocks[2])
        num_planes += nblocks[2]*growth_rate
        out_planes = int(math.floor(num_planes*reduction))
        self.trans3 = Transition(num_planes, out_planes)
        num_planes = out_planes

        self.dense4 = self._make_dense_layers(block, num_planes, nblocks[3])
        num_planes += nblocks[3]*growth_rate

        self.bn = nn.BatchNorm2d(num_planes)
        self.linear = nn.Linear(num_planes, num_classes)

    def _make_dense_layers(self, block, in_planes, nblock):
        layers = []
        for i in range(nblock):
            layers.append(block(in_planes, self.growth_rate))
            in_planes += self.growth_rate
        return nn.Sequential(*layers)

    def forward(self, x):
        out = self.conv1(x)
        out = self.trans1(self.dense1(out))
        out = self.trans2(self.dense2(out))
        out = self.trans3(self.dense3(out))
        out = self.dense4(out)
        out = F.avg_pool2d(F.relu(self.bn(out)), 4)
        out = out.view(out.size(0), -1)
        out = self.linear(out)
        return out


def get_cifar_small(
        batch_size=64,
        lr=0.05,
        momentum=0.9,
        cuda=False,
        data_path=expanduser('~/.davinci/data/'),
        model=None,
        valid=False,
        ):
    """
    A smaller DenseNet that trains in less than 30 seconds per epoch.
    """

    print('WARNING: The hyperparameters for this model are not well tuned.')

    if model is None:
        model = DenseNet(Bottleneck, [6, 6, 6, 6], growth_rate=6)

    if cuda:
        model.cuda()
        kwargs = {'num_workers': 4, 'pin_memory': True}
    else:
        kwargs = {}

    dataset = datasets.CIFAR10(root=data_path,
                               train=True,
                               download=True,
                               transform=transforms.Compose([
                                   transforms.ToTensor(),
                                   transforms.Normalize((0.4914, 0.4822, 0.4465),
                                                        (0.2023, 0.1994, 0.2010)),
                               ]))
    train_set = DataLoader(dataset,
                           batch_size=batch_size,
                           shuffle=True,
                           **kwargs)

    test_set = DataLoader(
            datasets.CIFAR10(data_path,
                             train=False,
                             transform=transforms.Compose([
                                 transforms.ToTensor(),
                                 transforms.Normalize((0.4914, 0.4822, 0.4465),
                                                      (0.2023, 0.1994, 0.2010)),
                             ])
            ),
            batch_size=batch_size,
            shuffle=False,
            **kwargs)

    loss = nn.CrossEntropyLoss()
    opt = optim.SGD(model.parameters(),
                    lr=lr,
                    momentum=momentum,
                    weight_decay=5e-4)

    num_epochs = 30
    scheduler = optim.lr_scheduler.StepLR(opt, 30, gamma=0.1)

    if valid:
        num_valid = len(test_set.dataset)
        num_train = len(dataset) - num_valid
        train_data, valid_data = split_dataset(dataset,
                                               [num_train, num_valid])
        train_set = DataLoader(train_data, batch_size=batch_size,
                               shuffle=True, **kwargs)
        valid_set = DataLoader(valid_data, batch_size=batch_size,
                               shuffle=False, **kwargs)
        return model, (train_set, valid_set, test_set), loss, opt, scheduler, num_epochs

    return model, (train_set, test_set), loss, opt, scheduler, num_epochs

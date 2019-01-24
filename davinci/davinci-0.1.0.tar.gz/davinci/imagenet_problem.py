#!/usr/bin/env python

"""
This example is largely inspired from the PyTorch example available at:
https://github.com/pytorch/examples/
"""

import os

import torch as th
import torch.nn as nn
import torch.optim as optim

from torch.utils.data import DataLoader
from torchvision import models, datasets, transforms

from .utils import split_dataset

IMAGENET_PATH = '/data/lisa/data/ImageNet2012_jpeg'
IMAGENET_PATH = '/media/seba-1511/Samsung/imagenet'


def get_imagenet(
        batch_size=256,
        lr=0.1,
        momentum=0.9,
        cuda=False,
        data_path=IMAGENET_PATH,
        model=None,
        valid=False,
        ):

    if model is None:
        model = models.resnet18()

    kwargs = {'num_workers': 12, 'pin_memory': True}
    if cuda:
        model.cuda()

    bsz = batch_size

    train_dir = os.path.join(data_path, 'train/')
    valid_dir = os.path.join(data_path, 'val/')
    valid_dir = os.path.join(data_path, 'valid/')
    normalize = transforms.Normalize(mean=[0.485, 0.456, 0.406],
                                     std=[0.229, 0.224, 0.225])

    train_data = datasets.ImageFolder(train_dir,
                                      transform=transforms.Compose([
                                          transforms.RandomResizedCrop(224),
                                          transforms.RandomHorizontalFlip(),
                                          transforms.ToTensor(),
                                          normalize,
                                      ]))

    train_set = th.utils.data.DataLoader(train_data,
                                         batch_size=bsz,
                                         shuffle=True,
                                         **kwargs)

    test_data = datasets.ImageFolder(valid_dir,
                                     transform=transforms.Compose([
                                         transforms.Resize(256),
                                         transforms.CenterCrop(224),
                                         transforms.ToTensor(),
                                         normalize,
                                        ]))

    test_set = th.utils.data.DataLoader(test_data,
                                        batch_size=bsz,
                                        shuffle=True,
                                        **kwargs)

    loss = nn.CrossEntropyLoss()
    if cuda:
        loss = loss.cuda()

    opt = optim.SGD(model.parameters(),
                    lr=lr,
                    momentum=momentum,
                    weight_decay=1e-4)
    scheduler = optim.lr_scheduler.StepLR(opt, step_size=30, gamma=0.1)
    num_epochs = 90

    if valid:
        num_valid = len(test_set.dataset)
        num_train = len(train_data) - num_valid
        train_data, valid_data = split_dataset(train_data,
                                               [num_train, num_valid])
        train_set = DataLoader(train_data, batch_size=batch_size,
                               shuffle=True, **kwargs)
        valid_set = DataLoader(valid_data, batch_size=batch_size,
                               shuffle=False, **kwargs)
        return model, (train_set, valid_set, test_set), loss, opt, scheduler, num_epochs


    return model, (train_set, test_set), loss, opt, scheduler, num_epochs

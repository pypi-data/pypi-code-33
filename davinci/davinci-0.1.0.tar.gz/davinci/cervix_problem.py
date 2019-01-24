#!/usr/bin/env python

import os

import torch as th
import torch.nn as nn
import torch.nn.functional as F
from torchvision import models, datasets, transforms

from .loss import L1, L2
from .datasets import DataPartitioner
from .utils import get_optimizer, get_dist

CERVIX_PATH = '/media/seba-1511/OCZ/cervical_cancer/'


def get_cervix(args):
    rank = args.rank
    size = args.size
    cuda = args.cuda

    model = models.resnet34()

    if size == 1:
        model = nn.DataParallel(model, device_ids=[0, 2])
        # model = nn.DataParallel(model, device_ids=[1, 3])

    kwargs = {'num_workers': 10, 'pin_memory': True}
    if cuda:
        model.cuda()
    else:
        kwargs = {}

    bsz = args.bsz // size

    # train_dir = os.path.join(CERVIX_PATH, 'additional')
    train_dir = os.path.join(CERVIX_PATH, 'train')
    valid_dir = os.path.join(CERVIX_PATH, 'train')
    normalize = transforms.Normalize(mean=[0.485, 0.456, 0.406],
                                     std=[0.229, 0.224, 0.225])

    train_data = datasets.ImageFolder(train_dir,
                                      transform=transforms.Compose([
                                          transforms.CenterCrop(224),
                                          transforms.RandomHorizontalFlip(),
                                          transforms.ToTensor(),
                                          normalize,
                                      ]))

    print('Partitioning...')
    partition = DataPartitioner(train_data, [0.9, 0.1])
    train_data = partition.use(0)
    train_part = DataPartitioner(
        train_data, [1.0 / size for _ in xrange(size)]).use(rank)
    train_set = th.utils.data.DataLoader(
        train_part, batch_size=bsz, shuffle=True, **kwargs)
    # train_set = th.utils.data.DataLoader(train_data, batch_size=bsz, shuffle=True, **kwargs)

    test_data = partition.use(1)
    # test_data = datasets.ImageFolder(valid_dir, transform=transforms.Compose([
    # transforms.Scale(256),
    # transforms.CenterCrop(224),
    # transforms.ToTensor(),
    # normalize,
    # ]))
    # test_part = DataPartitioner(test_data, [0.01, ]).use(0)
    # test_set = th.utils.data.DataLoader(test_part, batch_size=bsz, shuffle=False, **kwargs)
    test_set = th.utils.data.DataLoader(
        test_data, batch_size=bsz, shuffle=False, **kwargs)

    loss = nn.CrossEntropyLoss()
    if cuda:
        loss = loss.cuda()

    if args.regL == 1:
        loss = L1(loss, model.parameters(), lam=args.lam)
    if args.regL == 2:
        loss = L2(loss, model.parameters(), lam=args.lam)

    # sgd = SGD(model.parameters(), lr=args.lr, momentum=0.9, weight_decay=1e-4)
    # opt = sgd
    # opt = ImpHessianSVD(sgd, delta=0.001)
    opt = get_optimizer(args, model.parameters())

    num_epochs = args.epochs

    return model, (train_set, test_set), loss, opt, num_epochs

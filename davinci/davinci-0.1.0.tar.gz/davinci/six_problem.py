#!/usr/bin/env python

import torch as th
import torch.nn as nn
import torch.nn.functional as F
import torch.optim as optim
from torchvision import datasets, transforms, models

from .datasets import SixHumps, DataPartitioner
from .utils import FuncNet, get_optimizer, get_dist


def get_six_humps(args):
    cuda = args.cuda
    rank = args.rank
    size = args.size
    params = (nn.Linear(2, 15), nn.Linear(15, 1))

    def forward(self, x):
        x = self.params[0](x)
        x = F.sigmoid(x)
        return self.params[1](x)

    model = FuncNet(params, forward)

    if cuda:
        model.cuda()
        kwargs = {'num_workers': 1, 'pin_memory': True}
    else:
        kwargs = {}

    partition_sizes = [1.0 / size for _ in range(size)]
    partition = DataPartitioner(
        SixHumps(num_samples=10000), partition_sizes).use(rank)
    train_set = th.utils.data.DataLoader(partition,
                                         batch_size=args.bsz, shuffle=True,
                                         **kwargs)

    test_set = th.utils.data.DataLoader(SixHumps(num_samples=2000),
                                        batch_size=64, shuffle=True, **kwargs)

    # loss = nn.MSELoss()
    loss = F.smooth_l1_loss

    sgd = optim.SGD(model.parameters(), lr=0.1)
    sgd.name = 'SGD'
    optimizers = (
        sgd,
        Dist(SGD(model.parameters(), alpha=0.1)),
        HessianSVD(SGD(model.parameters(), alpha=0.1)),
    )

    num_epochs = args.epochs

    return model, (train_set, test_set), loss, optimizers, num_epochs

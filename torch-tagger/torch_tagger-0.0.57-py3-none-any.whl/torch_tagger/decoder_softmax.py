# -*- coding: utf-8 -*-
"""
.. module:: decoder_softmax

"""

import torch
from torch import nn

from .utils import sequence_mask


class DecoderSoftmax(nn.Module):
    """Softmax loss and inference
    """

    def __init__(self):
        """init"""
        super(DecoderSoftmax, self).__init__()
        self._cross_entropy_loss = nn.CrossEntropyLoss(
            ignore_index=0, reduction='sum')

    def compute_loss(self, encoder_output, tags, lengths):
        """Softmax loss"""
        batch_size, seq_len = encoder_output.size()[:2]
        seq_len = encoder_output.size(1)
        masks = sequence_mask(lengths, seq_len)
        encoder_output = encoder_output * masks.view(batch_size, seq_len, 1)
        tags = tags * masks.long()
        encoder_output = encoder_output.view(batch_size * seq_len, -1)
        tags = tags.view(-1)
        return self._cross_entropy_loss(encoder_output, tags)

    def forward(self, encoder_output):
        """Softmax Result"""
        scores = encoder_output.max(dim=2)
        _, pred = torch.max(encoder_output, dim=2)
        return scores, pred.cpu().detach().numpy()

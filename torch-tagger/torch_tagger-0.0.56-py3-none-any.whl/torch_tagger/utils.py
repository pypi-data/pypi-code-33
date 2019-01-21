# -*- coding: utf-8 -*-
"""Utils tools for tagger
Created by InfinityFuture
"""

import re
import sys
from typing import Optional, Tuple

import torch

if torch.cuda.is_available():
    print('CUDA is online', file=sys.stderr)
else:
    print('CUDA is offline', file=sys.stderr)

DEVICE = torch.device('cuda' if torch.cuda.is_available() else 'cpu')


def normalize_word(word: str) -> str:
    """normalize number"""
    word = re.sub(r'\d', '0', word)
    return word


def text_reader(path: str) -> Tuple[list, list]:
    """Read a text file, and return data
    data should follow this format:

    I O
    want O
    to O
    New B-City
    York I-City
    """
    with open(path, 'r') as fobj:
        parts = fobj.read().split('\n\n')
        parts = [part.strip() for part in parts]
        parts = [part for part in parts if len(part) > 0]
    assert parts, 'text file empty "{}"'.format(path)

    x_data = []
    y_data = []
    for part in parts:
        lines = part.split('\n')
        lines = [line.split() for line in lines]
        words = [x[0] for x in lines]
        tags = [x[-1] for x in lines]
        words = [normalize_word(word) for word in words]
        x_data.append(words)
        y_data.append(tags)
        assert len(words) == len(tags), \
            'line "{}" and "{}" do not match "{}" vs "{}"'.format(
                len(words), len(tags), words, tags)
    return x_data, y_data


def sequence_mask(lens: torch.Tensor,
                  max_len: Optional[int] = None) -> torch.FloatTensor:
    """InfinityFutures: This function is copy from:

    https://github.com/epwalsh/pytorch-crf

    The author is epwalsh, and its license is MIT too

    Compute sequence mask.

    Parameters

    lens : torch.Tensor
        Tensor of sequence lengths ``[batch_size]``.
    max_len : int, optional (default: None)
        The maximum length (optional).

    Returns

    torch.ByteTensor
        Returns a tensor of 1's and 0's of size ``[batch_size x max_len]``.
    """
    batch_size = lens.size(0)

    if max_len is None:
        max_len = lens.max().item()

    ranges = torch.arange(0, max_len, device=lens.device).long()
    ranges = ranges.unsqueeze(0).expand(batch_size, max_len)
    ranges = torch.autograd.Variable(ranges)

    lens_exp = lens.unsqueeze(1).expand_as(ranges)
    mask = ranges < lens_exp

    return mask.float()


def extract_entities(seq: list, x=None) -> list:
    """Extract entities from a sequences

    ---
    input: ['B', 'I', 'I', 'O', 'B', 'I']
    output: [(0, 3, ''), (4, 6, '')]
    ---
    input: ['B-loc', 'I-loc', 'I-loc', 'O', 'B-per', 'I-per']
    output: [(0, 3, '-loc'), (4, 6, '-per')]
    ---
    input:
        seq=['B-loc', 'I-loc', 'I-loc', 'O', 'B-per', 'I-per']
        x='我爱你欧巴桑'
    output:
        [(0, 3, '-loc', '我爱你'), (4, 6, '-per', '巴桑')]
    """
    ret = []
    start_ind, start_type = -1, None
    for i, tag in enumerate(seq):
        if tag.startswith('S'):
            if x is not None:
                ret.append((i, i + 1, tag[1:], x[i:i + 1]))
            else:
                ret.append((i, i + 1, tag[1:]))
            start_ind, start_type = -1, None
        if tag.startswith('B') or tag.startswith('O'):
            if start_ind >= 0:
                if x is not None:
                    ret.append((start_ind, i, start_type, x[start_ind:i]))
                else:
                    ret.append((start_ind, i, start_type))
                start_ind, start_type = -1, None
        if tag.startswith('B'):
            start_ind = i
            start_type = tag[1:]
    if start_ind >= 0:
        if x is not None:
            ret.append((start_ind, len(seq), start_type, x[start_ind:]))
        else:
            ret.append((start_ind, len(seq), start_type))
        start_ind, start_type = -1, None
    return ret

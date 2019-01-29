"""
.. module:: char_cnn

Char + CNN Features

Basically copy from:
https://github.com/jiesutd/NCRFpp/blob/master/model/charbilstm.py

"""

import torch
import torch.nn.functional as F
from torch import nn


class CharCNN(torch.nn.Module):
    """Use CNN to extract char features
    """

    def __init__(self, char_vocab_size, char_max_len, char_embedding_dim,
                 char_hidden_dim, char_dropout_p, device, embedding_trainable):
        """init
        """
        super(CharCNN, self).__init__()
        self._char_vocab_size = char_vocab_size
        self._char_max_len = char_max_len
        self._char_embedding_dim = char_embedding_dim
        self._char_hidden_dim = char_hidden_dim
        self._char_dropout_p = char_dropout_p
        self._device = device
        self._embedding_trainable = embedding_trainable

        self._char_cnn = nn.Conv1d(
            char_embedding_dim, char_hidden_dim, kernel_size=3, padding=1)

        self._char_dropout = nn.Dropout(self._char_dropout_p)
        self._char_embeds = nn.Embedding(
            char_vocab_size, char_embedding_dim, padding_idx=0)
        self._char_embeds.weight.requires_grad = self._embedding_trainable

    def forward(self, chars, charlens=None):
        assert len(chars.size()) == 3
        batch_size = chars.size(0)
        seq_len = chars.size(1)
        total_word = batch_size * seq_len
        chars = chars.view(total_word, self._char_max_len)
        char_feats = self._char_embeds(chars)
        char_feats = self._char_dropout(char_feats)
        char_feats = char_feats.transpose(2, 1)
        char_feats = self._char_cnn(char_feats)
        char_feats = F.max_pool1d(char_feats, char_feats.size(2))
        char_feats = char_feats.view(batch_size, seq_len,
                                     self._char_hidden_dim)

        return char_feats

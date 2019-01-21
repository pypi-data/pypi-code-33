"""
.. module:: char_rnn

Char + RNN Features

"""

import torch
from torch import nn


class CharRNN(nn.Module):
    """Use RNN to extract char features
    """

    def __init__(self, char_vocab_size, char_max_len, char_embedding_dim,
                 char_hidden_dim, char_dropout_p, char_bidirectional, rnn_type,
                 device, embedding_trainable):
        """init"""
        super(CharRNN, self).__init__()
        self._char_vocab_size = char_vocab_size
        self._char_max_len = char_max_len
        self._char_embedding_dim = char_embedding_dim
        self._char_hidden_dim = char_hidden_dim
        self._char_dropout_p = char_dropout_p
        self._char_bidirectional = char_bidirectional
        self._rnn_type = rnn_type
        self._device = device
        self._embedding_trainable = embedding_trainable

        self._char_directions = 2 if char_bidirectional else 1
        self._char_dropout = nn.Dropout(self._char_dropout_p)
        self._char_embeds = nn.Embedding(
            char_vocab_size, char_embedding_dim, padding_idx=0)
        self._char_embeds.weight.requires_grad = self._embedding_trainable

        if rnn_type == 'lstm':
            self._char_rnn = nn.LSTM(
                char_embedding_dim,
                char_hidden_dim // self._char_directions,
                num_layers=1,
                bidirectional=char_bidirectional)
        elif rnn_type == 'gru':
            self._char_rnn = nn.GRU(
                char_embedding_dim,
                char_hidden_dim // self._char_directions,
                num_layers=1,
                bidirectional=char_bidirectional)

    def forward(self, chars, charlens):
        assert len(chars.size()) == 3
        batch_size = chars.size(0)
        seq_len = chars.size(1)
        char_len = chars.size(2)
        total_word = batch_size * seq_len
        chars = chars.view(total_word, char_len)
        chars_lengths = charlens.view(total_word)
        chars_lengths, perm_index = chars_lengths.sort(0, descending=True)

        # char_feats dim: [total_word, char_len, char_embedding_size]
        char_feats = self._char_embeds(chars)
        # dropout char embedding
        char_feats = self._char_dropout(char_feats)
        char_feats = char_feats[perm_index]
        char_feats = char_feats[chars_lengths > 0]
        chars_lengths = chars_lengths[chars_lengths > 0]

        char_feats = char_feats.transpose(1, 0)
        char_feats = nn.utils.rnn.pack_padded_sequence(
            char_feats, chars_lengths, batch_first=False)

        # Get last hidden as features
        char_feats, char_hidden = self._char_rnn(char_feats)
        # char_hidden dim: [directions, total_word - padding, hidden_dim]
        if isinstance(char_hidden, tuple):
            char_hidden = char_hidden[0]

        # char_hidden dim: [total_word - padding, directions, hidden_dim]
        char_hidden = char_hidden.transpose(1, 0)
        # char_hidden dim: [total_word - padding, directions * hidden_dim]
        char_hidden = char_hidden.contiguous().view(char_hidden.size(0), -1)

        char_feats, _ = nn.utils.rnn.pad_packed_sequence(
            char_feats, batch_first=True, total_length=self._char_max_len)

        char_feats = char_hidden
        pad_length = total_word - char_feats.size(0)
        pad = torch.zeros((pad_length, char_feats.size(1)),
                          device=self._device)
        char_feats = torch.cat([char_feats, pad], dim=0)

        char_feats[perm_index] = char_feats[torch.arange(0, len(char_feats))]

        char_feats = char_feats.contiguous().view(batch_size, seq_len,
                                                  self._char_hidden_dim)
        return char_feats

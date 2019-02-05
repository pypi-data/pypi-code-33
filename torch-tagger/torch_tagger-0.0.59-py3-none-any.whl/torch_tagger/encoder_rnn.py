# -*- coding: utf-8 -*-
"""
.. module:: encoder_rnn

"""

import torch
from torch import nn


class EncoderRNN(nn.Module):
    """Use RNN to encode the word
    """

    def __init__(self, vocab_size, tag_to_ix, embedding_dim, hidden_dim,
                 num_layers, bidirectional, embedding_dropout_p, rnn_dropout_p,
                 rnn_type, embedding_trainable, use_char, char_hidden_dim):
        """
        Word Embedding and RNN
        """
        super(EncoderRNN, self).__init__()

        if rnn_type not in ('lstm', 'gru'):
            raise Exception('Invalid rnn_type')

        self._vocab_size = vocab_size
        self._tag_to_ix = tag_to_ix
        self._embedding_dim = embedding_dim
        self._hidden_dim = hidden_dim
        self._num_layers = num_layers
        self._bidirectional = bidirectional
        self._embedding_dropout_p = embedding_dropout_p
        self._rnn_dropout_p = rnn_dropout_p
        self._rnn_type = rnn_type
        self._embedding_trainable = embedding_trainable
        self._use_char = use_char
        self._char_hidden_dim = char_hidden_dim

        self._tagset_size = len(tag_to_ix)
        self._directions = 2 if bidirectional else 1
        self._embedding_dropout = nn.Dropout(p=self._embedding_dropout_p)
        self._rnn_dropout = nn.Dropout(p=self._rnn_dropout_p)

        # Embedding Layer
        self._word_embeds = nn.Embedding(
            vocab_size, embedding_dim, padding_idx=0)
        self._word_embeds.weight.requires_grad = self._embedding_trainable

        input_size = embedding_dim
        if use_char:
            input_size += char_hidden_dim

        # RNN Layer
        if rnn_type == 'lstm':
            self._rnn = nn.LSTM(
                input_size,
                hidden_dim // self._directions,
                num_layers=num_layers,
                bidirectional=bidirectional,
                dropout=rnn_dropout_p if num_layers > 1 else 0)
        elif rnn_type == 'gru':
            self._rnn = nn.GRU(
                input_size,
                hidden_dim // self._directions,
                num_layers=num_layers,
                bidirectional=bidirectional,
                dropout=rnn_dropout_p if num_layers > 1 else 0)

        # Tag projection
        self._hidden2tag = nn.Linear(hidden_dim, self._tagset_size)

    def load_embedding(self, pretrained_embedding):
        """Load other pre-trained embedding vectors"""
        word_embeds = self._word_embeds
        assert len(pretrained_embedding.shape) == 2
        # import pdb; pdb.set_trace()
        assert pretrained_embedding.shape[0] == word_embeds.weight.size(0)
        assert pretrained_embedding.shape[1] == word_embeds.weight.size(1)
        print('loaded pre-trained vectors', pretrained_embedding.shape)
        pretrained_embedding = torch.from_numpy(pretrained_embedding)
        word_embeds.weight.data.copy_(pretrained_embedding)
        word_embeds.weight.requires_grad = self._embedding_trainable

    def forward(self, sentence, lengths, char_feats=None):
        """Get the output of RNN model"""
        # sentence dim: [batch_size, seq_len]
        batch_size, seq_len = sentence.size()
        # embeds dim: [batch_size, seq_len, embedding_size]
        embeds = self._word_embeds(sentence)
        if char_feats is not None:
            embeds = torch.cat([embeds, char_feats], 2)
        embeds = self._embedding_dropout(embeds)
        # embeds dim: [seq_len, batch_size, embedding_size]
        embeds = embeds.transpose(1, 0)

        packed = nn.utils.rnn.pack_padded_sequence(
            embeds, lengths, batch_first=False)
        rnn_out, _ = self._rnn(packed)
        # rnn_out dim: [batch_size, seq_len, hidden_dim]
        rnn_out, _ = nn.utils.rnn.pad_packed_sequence(
            rnn_out, batch_first=True)
        rnn_out = self._rnn_dropout(rnn_out)
        # rnn_feats dim: [batch_size, seq_len, target_dim]
        rnn_feats = self._hidden2tag(rnn_out)
        ret = rnn_feats.view(batch_size, seq_len, -1)
        return ret

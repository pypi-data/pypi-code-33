# -*- coding: utf-8 -*-
"""
.. module:: tagger_model

Based https://pytorch.org/tutorials/beginner/nlp/advanced_tutorial.html

Modified by InfinityFuture

"""

from torch import nn

from .char_cnn import CharCNN
from .char_rnn import CharRNN
from .decoder_crf import DecoderCRF
from .decoder_softmax import DecoderSoftmax
from .encoder_rnn import EncoderRNN
from .utils import sequence_mask


class TaggerModel(nn.Module):
    """Sequence Tagger Model
    """

    def __init__(self, vocab_size, tag_to_ix, embedding_dim, hidden_dim,
                 num_layers, bidirectional, embedding_dropout_p, rnn_dropout_p,
                 rnn_type, embedding_trainable, use_crf, use_char,
                 char_vocab_size, char_max_len, char_embedding_dim,
                 char_hidden_dim, char_dropout_p, char_bidirectional,
                 average_loss):
        """
        Embedding Random Init:

        [He et al.2015] Kaiming He, Xiangyu Zhang, Shaoqing
        Ren, and Jian Sun. 2015. Delving deep into recti-
        fiers: Surpassing human-level performance on ima-
        genet classification. In Proceedings of the IEEE In-
        ternational Conference on Computer Vision, pages
        1026–1034.
        """
        super(TaggerModel, self).__init__()

        if rnn_type not in ('lstm', 'gru'):
            raise Exception('Invalid rnn_type')

        self._use_crf = use_crf
        self._average_loss = average_loss

        self._encoder = EncoderRNN(
            vocab_size, tag_to_ix, embedding_dim, hidden_dim, num_layers,
            bidirectional, embedding_dropout_p, rnn_dropout_p, rnn_type,
            embedding_trainable, use_char, char_hidden_dim)

        if use_crf:
            self._decoder = DecoderCRF(tag_to_ix)
        else:
            self._decoder = DecoderSoftmax()

        self._char_features = None
        if isinstance(use_char, str):
            if use_char.lower() == 'rnn':
                self._char_features = CharRNN(
                    char_vocab_size, char_max_len, char_embedding_dim,
                    char_hidden_dim, char_dropout_p, char_bidirectional,
                    rnn_type, embedding_trainable)
            elif use_char.lower() == 'cnn':
                self._char_features = CharCNN(
                    char_vocab_size, char_max_len, char_embedding_dim,
                    char_hidden_dim, char_dropout_p, embedding_trainable)

    def load_embedding(self, pretrained_embedding):
        """Load other pre-trained embedding vectors"""
        self._encoder.load_embedding(pretrained_embedding)

    def compute_loss(self, sentence, tags, lengths, chars=None, charlens=None):
        """Compute Train Loss"""
        char_feats = None
        sentence = sentence.long()
        tags = tags.long()
        lengths = lengths.long()
        if chars is not None and self._char_features is not None:
            chars = chars.long()
            charlens = charlens.long()
            char_feats = self._char_features(chars, charlens)
        encoder_output = self._encoder(
            sentence, lengths, char_feats=char_feats)
        loss = self._decoder.compute_loss(encoder_output, tags, lengths)
        if self._average_loss:
            batch_size = sentence.size(0)
            loss /= batch_size
        return loss

    def forward(self, sentence, lengths, chars=None, charlens=None):
        """Main forward function, predict only"""

        sentence = sentence.long()
        lengths = lengths.long()

        char_feats = None
        if chars is not None and self._char_features is not None:
            chars = chars.long()
            charlens = charlens.long()
            char_feats = self._char_features(chars, charlens)

        # Get the emission scores from the BiLSTM
        rnn_feats = self._encoder(sentence, lengths, char_feats=char_feats)
        seq_len = rnn_feats.size(1)
        masks = sequence_mask(lengths, seq_len)

        if self._use_crf:
            # CRF
            # Find the best path, given the features.
            return self._decoder(rnn_feats, lengths, masks)
        # Softmax
        return self._decoder(rnn_feats)

import json
import os
from collections import Counter

import numpy as np
import torch

# from pypinyin import lazy_pinyin

CURRENT_DIR = os.path.realpath(os.path.dirname(__file__))
WORD_ORDER = json.load(open(os.path.join(CURRENT_DIR, 'word_orders.json')))
DEVICE = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
START_TAG = '<START>'
STOP_TAG = '<STOP>'
PAD_TAG = '<PAD>'
UNK_TAG = '<UNK>'


class LanguageModel(object):
    def __init__(
            self,
            use_char: bool = True,
            limit: int = 1,
            max_len: int = 500,
            pad: int = 0,
            pad_method: str = 'right',
            char_pad_method: str = 'right',
            char_max_len: int = 20,
            _word_to_ix=None,
            _ix_to_word=None,
            _char_to_ix=None,
            _ix_to_char=None,
    ):
        self.use_char = use_char
        self.limit = limit
        self.word_to_ix = None
        self.ix_to_word = None
        self.char_to_ix = None
        self.ix_to_char = None
        if _word_to_ix is not None:
            self.word_to_ix = _word_to_ix
        if _ix_to_char is not None:
            self.ix_to_word = _ix_to_char
        if _char_to_ix is not None:
            self.char_to_ix = _char_to_ix
        if _ix_to_char is not None:
            self.ix_to_char = _ix_to_char
        self.max_len = max_len
        self.pad = pad
        self.pad_method = pad_method
        self.char_pad_method = char_pad_method
        self.char_max_len = char_max_len
        self.START_TAG = START_TAG
        self.STOP_TAG = STOP_TAG
        self.PAD_TAG = PAD_TAG
        self.UNK_TAG = UNK_TAG

    def fit(self, seqs: list):
        sentence_word = Counter()
        sentence_word_char = Counter()
        for sentence in seqs:
            sentence_word.update(sentence)

        word_to_ix = {PAD_TAG: 0, UNK_TAG: 1, START_TAG: 2, STOP_TAG: 3}
        for word, count in sentence_word.items():
            sentence_word_char.update(list(word))
            if word not in word_to_ix and count >= self.limit:
                indx = len(word_to_ix)
                word_to_ix[word] = indx

        sentence_word_char = Counter('abcdefghijklmnopqrstuvwxyz ' '一丨フノ丶')

        char_to_ix = {PAD_TAG: 0, UNK_TAG: 1, START_TAG: 2, STOP_TAG: 3}

        for char, count in sentence_word_char.items():
            indx = len(char_to_ix)
            char_to_ix[char] = indx

        ix_to_char = {v: k for k, v in char_to_ix.items()}
        ix_to_word = {v: k for k, v in word_to_ix.items()}

        if self.word_to_ix is None:
            self.word_to_ix = word_to_ix
            self.ix_to_word = ix_to_word
        if self.char_to_ix is None:
            self.char_to_ix = char_to_ix
            self.ix_to_char = ix_to_char

    def transform(self, X, max_len=None):
        ret = []
        for x in X:
            x = self.prepare_sequence(x)
            x = self.pad_seq(x, max_len)
            ret.append(x)
        ret = np.asarray(ret)
        return ret

    def inverse_transform(self, X, no_pad=True, no_unk=True):
        ret = []
        for x in X:
            x = [self.ix_to_word[i] for i in x]
            if no_pad:
                x = [i for i in x if i != PAD_TAG]
            if no_unk:
                x = [i for i in x if i != UNK_TAG]
            ret.append(x)
        return ret

    def char_transform(self, seqs: list, max_len=None):
        """extract char features"""
        char_max_len = self.char_max_len
        if max_len is None:
            max_len = self.max_len
        char_to_ix = self.char_to_ix

        char_batch = np.zeros((len(seqs), max_len, char_max_len))
        char_len_batch = np.zeros((len(seqs), max_len))

        for ix, seq in enumerate(seqs):
            seq = [x if x not in WORD_ORDER else WORD_ORDER[x] for x in seq]
            for jx, char in enumerate(seq):
                char = char[:char_max_len]
                char = self.prepare_sequence(char, char_to_ix)
                char = self.pad_seq(
                    char, char_max_len, method=self.char_pad_method)
                np.copyto(char_batch[ix][jx], char)
                char_len_batch[ix][jx] = len(char)
        return char_batch, char_len_batch

    def pad_seq(self, seq: list, max_len=None, method=None) -> list:
        """Padding data to max_len length"""
        if max_len is None:
            max_len = self.max_len
        if method is None:
            method = self.pad_method
        pad = self.pad
        if method == 'right':
            if len(seq) < max_len:
                seq = seq + [pad] * (max_len - len(seq))
        elif method == 'left':
            if len(seq) < max_len:
                seq = [pad] * (max_len - len(seq)) + seq
        elif method == 'both':
            if len(seq) < max_len:
                for i in range(max_len - len(seq)):
                    if i % 2 == 0:
                        seq = seq + [pad]
                    else:
                        seq = [pad] + seq
        return seq

    def prepare_sequence(self, seq: list, to_ix=None) -> list:
        """Convert sequence to indices"""
        if to_ix is None:
            to_ix = self.word_to_ix
        idxs = [to_ix[w] if w in to_ix else to_ix[UNK_TAG] for w in seq]
        return idxs


class TagModel(LanguageModel):
    def __init__(self):
        super().__init__(use_char=False, limit=0, max_len=1)


def test():
    lm = LanguageModel(max_len=20, char_max_len=10)
    x = ['我爱北京天安门', '我也爱北京']
    lm.fit(x)
    ret = lm.transform(x)
    cret = lm.char_transform(x)
    print('ret')
    print(ret)
    print('cret')
    print(cret)
    org = lm.inverse_transform(ret)
    print('restore')
    print(org)
    y = ['IOB', 'BBIO']
    lmy = TagModel()
    lmy.fit(y)
    rety = lmy.transform(y)
    print(rety)
    print(lmy.inverse_transform(rety))


if __name__ == '__main__':
    test()

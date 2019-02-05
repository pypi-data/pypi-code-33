import math

import numpy as np
from torch.utils.data import DataLoader, Dataset


class BatchSampler(object):
    def __init__(self, X, batch_size, shuffle=True):
        self.batch_size = batch_size
        self.len = math.ceil(len(X) / batch_size)
        self.total = len(X)
        self.pointers = [x * batch_size for x in list(range(self.len))]
        np.random.shuffle(self.pointers)

    def __iter__(self):
        for p in self.pointers:
            inds = []
            for i in range(self.batch_size):
                if i + p < self.total:
                    inds.append(i + p)
            yield inds

    def __len__(self):
        return len(self.pointers)


def data_iter(X, y, max_len, sentence_lm, tag_lm, batch_size=32):
    ds = TaggerDataset(X, y, max_len, sentence_lm, tag_lm)

    return DataLoader(
        ds,
        batch_sampler=BatchSampler(X, batch_size),
        collate_fn=collate_fn,
        num_workers=4)


def collate_fn(data):
    # import pdb; pdb.set_trace()
    data = list(data)
    data = sorted(data, key=lambda x: x[0].shape[1], reverse=True)
    max_len = data[0][0].shape[1]
    for x in data:
        if x[0].shape[1] > max_len:
            max_len = x[0].shape[1]
    x_b = []
    y_b = []
    l_c = None if data[0][3] is None else []
    ll_c = None if data[0][4] is None else []
    for x in data:
        if x[0].shape[1] < max_len:
            x_0 = np.concatenate(
                [x[0], np.zeros((1, max_len - x[0].shape[1]))], axis=1)
        else:
            x_0 = x[0]
        x_b.append(x_0)

        if x[1].shape[1] < max_len:
            x_1 = np.concatenate(
                [x[1], np.zeros((1, max_len - x[1].shape[1]))], axis=1)
        else:
            x_1 = x[1]
        y_b.append(x_1)

        if x[3] is not None:
            if x[3].shape[1] < max_len:
                x_3 = np.concatenate([
                    x[3],
                    np.zeros((1, max_len - x[3].shape[1], x[3].shape[2]))
                ],
                                     axis=1)
            else:
                x_3 = x[3]
            l_c.append(x_3)

        if x[4] is not None:
            if x[4].shape[1] < max_len:
                x_4 = np.concatenate(
                    [x[4], np.zeros((1, max_len - x[4].shape[1]))], axis=1)
            else:
                x_4 = x[4]
            ll_c.append(x_4)

    x_b = np.concatenate(x_b)
    y_b = np.concatenate(y_b)
    l_b = np.concatenate([x[2] for x in data])
    l_c = np.concatenate(l_c) if l_c is not None else None
    ll_c = np.concatenate(ll_c) if ll_c is not None else None
    return x_b, y_b, l_b, l_c, ll_c


class TaggerDataset(Dataset):
    def __init__(self, x_data, y_data, max_limit, sentence_lm, tag_lm):
        data = list(zip(x_data, y_data))
        data = sorted(data, key=lambda x: len(x[0]), reverse=True)
        self.x_data, self.y_data = zip(*data)
        self.max_limit = max_limit
        self._sentence_lm = sentence_lm
        self._tag_lm = tag_lm

    def __len__(self):
        return len(self.x_data)

    def __getitem__(self, i):
        x_batch = [self.x_data[i][:self.max_limit]]
        y_batch = [self.y_data[i][:self.max_limit]]

        len_batch = [len(t) for t in x_batch]
        max_len = np.max(len_batch)

        char_batch = None
        char_len_batch = None
        if self._sentence_lm.use_char:
            char_batch, char_len_batch = \
                self._sentence_lm.char_transform(x_batch, max_len)
            x_batch = self._sentence_lm.transform(x_batch, max_len)
            y_batch = self._tag_lm.transform(y_batch, max_len)
            batches = list(
                zip(x_batch, y_batch, len_batch, char_batch, char_len_batch))
            batches = sorted(batches, key=lambda x: x[2], reverse=True)
            (x_batch, y_batch, len_batch, char_batch,
             char_len_batch) = zip(*batches)

            tcx, tcy, tcl, tcc, tccl = (np.asarray(x_batch),
                                        np.asarray(y_batch),
                                        np.asarray(len_batch),
                                        np.asarray(char_batch),
                                        np.asarray(
                                            char_len_batch, dtype=np.int32))
            return tcx, tcy, tcl, tcc, tccl
        else:
            x_batch = self._sentence_lm.transform(x_batch, max_len)
            y_batch = self._tag_lm.transform(y_batch, max_len)
            batches = list(zip(x_batch, y_batch, len_batch))
            batches = sorted(batches, key=lambda x: x[2], reverse=True)
            (x_batch, y_batch, len_batch) = zip(*batches)

            tcx, tcy, tcl = (np.asarray(x_batch), np.asarray(y_batch),
                             np.asarray(len_batch))
            return tcx, tcy, tcl, None, None

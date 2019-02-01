# -*- coding: utf-8 -*-

__author__ = 'sv99'

import os

from tralutils.tools import read_datetime, read_uint, sizeof_fmt


# MSN_ID3_REC
# 0 byte channel
# 1 byte count_activ
# 2 byte reserved = 0
# 3 byte pos_ext - расширение поля pos для файлов длиной до 1Гб (адрес размером 40 бит)
# 4 4 byte time - unix format
# 8 4 byte pos - позиция в соответствующем файле msn3
# 12 12 byte - массив из 6 T_ID3_ACTIV
class MSN_ID3_REC:
    def __init__(self, data, pos):
        self.channel = data[pos]
        self.count_activ = data[pos + 1]
        self.pos_ext = data[pos + 3]
        self.time = read_datetime(data, pos + 4)
        self.pos = read_uint(data, pos + 8)
        self.activ = []
        for i in range(6):
            self.activ.append(T_ID3_ACTIV(data[pos + 12 + i * 2], data[pos + 12 + i * 2 + 1]))


# T_ID3_ACTIV
# byte channel
# byte value - максимальное значение активности для канала между индексными позициями
class T_ID3_ACTIV:
    def __init__(self, channel, value):
        self.channel = channel
        self.value = value


class IdxFile:
    def __init__(self, path, verbose=False):
        self.filename = path
        self._readed = False
        self._parsed = False
        self.data = None
        self.size = 0
        self.rec = []
        self.verbose = verbose

    @property
    def parsed(self):
        return self._parsed

    def parse(self):
        if self.verbose:
            print("parsing..")

        with open(self.filename, 'rb') as fp:
            self.data = bytearray(fp.read())
            self.size = len(self.data)

            pos = 0
            while pos < self.size:

                self.rec.append(MSN_ID3_REC(self.data, pos))
                pos += 24

        self._parsed = True
        if self.verbose:
            print("parsed %d records" % len(self.rec))
            print("OK")

    def read_rec(self):
        pass

    def dump(self):
        print("%s Size: %s" % (os.path.basename(self.filename), sizeof_fmt(self.size)))
        if len(self.rec) > 0:
            rec = self.rec[0]
            print("count: %i" % len(self.rec))
            print(rec.time.strftime("first: %d.%m.%Y %H:%M") + " msn3 pos: %d" % rec.pos)
            if len(self.rec) > 1:
                rec = self.rec[-1]
                print(rec.time.strftime("last:  %d.%m.%Y %H:%M") + " msn3 pos: %d" % rec.pos)
        else:
            print("empty file")
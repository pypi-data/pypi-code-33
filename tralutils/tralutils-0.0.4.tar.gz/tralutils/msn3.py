# -*- coding: utf-8 -*-

__author__ = 'sv99'

import os
from tralutils.tools import read_datetime, read_uint, read_ushort, read_string, sizeof_fmt

T_UNDEF = 0x00
T_VIDEO = 0x01
T_AUDIO = 0x02
T_TEXT = 0x04
T_IMAGE = 0x08
T_BINARY = 0x10

HDR_T_SIGN = 0xB505B5B5
IDX_T_SIGN = 0xB5B5B505


# HDR_T - заголовок с описанием потока
# 0 4 byte - signature HDR_T_SIGN
# 4 2 byte - длина заголовка с учетом сигнатуры
# 6 2 byte - длина расширения, описываемого структурой CONFIG_T
# 8 string - название устройства
# array of STREAM_T
# CONFIG_T
class HDR_T:
    def __init__(self, data, pos):
        self.header_len = read_ushort(data, pos + 4)
        self.config_len = read_ushort(data, pos + 6)
        self.size = self.header_len + self.config_len
        pos_config = pos + self.header_len

        pos, self.device_name = read_string(data, pos + 8)
        self.streams = []
        while pos < pos_config:
            stream = STREAM_T(data, pos)
            pos += stream.size
            self.streams.append(stream)
        self.config = CONFIG_T(data, pos_config)
        pass


class STREAM_T:
    def __init__(self, data, pos):
        self.number = data[pos]
        self.type = data[pos + 1]
        pos, self.alg_name = read_string(data, pos + 2)
        pos, self.stream_name = read_string(data, pos)
        pos, self.alg_params = read_string(data, pos)
        self.size = pos


class CONFIG_T:
    def __init__(self, data, pos):
        self.number = data[pos]
        self.type = data[pos + 1]
        pos, self.alg_name = read_string(data, pos + 2)
        pos, self.stream_name = read_string(data, pos)
        pos, self.alg_params = read_string(data, pos)
        self.size = pos


# IDX_T - индексная позиция
class IDX_T:
    def __init__(self, data, pos):
        self.channel = data[pos]
        self.count_activ = data[pos + 1]
        self.pos_ext = data[pos + 3]
        self.time = read_datetime(data, pos + 4)
        self.pos = read_uint(data, pos + 8)
        self.activ = []
        self.size = 0


# STREAM_T - описание потока

# DATA_T - данные потоков

# CONFIG_T - дополнительные параметры системы архивации


class Msn3File:
    def __init__(self, path, verbose=False):
        self.filename = path
        self._parsed = False
        self.data = None
        self.size = 0
        self.chunks = []
        self.verbose = verbose

    @property
    def parsed(self):
        return self._parsed

    @property
    def device_name(self):
        if len(self.chunks) > 0:
            if type(self.chunks[0]) is HDR_T:
                return self.chunks[0].device_name
        return "Unknown"

    def read(self):
        with open(self.filename, 'rb') as fp:
            self.data = bytearray(fp.read())
            self.size = len(self.data)

    def parse(self):
        if self.verbose:
            print("parsing..")
        self.read()

        pos = 0
        while pos < self.size:
            sign = read_uint(self.data, pos)
            if sign == HDR_T_SIGN:
                ch = HDR_T(self.data, pos)
                pos += ch.size
                self.chunks.append(ch)
            elif sign == IDX_T_SIGN:
                ch = IDX_T(self.data, pos)
                pos += ch.size
                self.chunks.append(ch)


        self._parsed = True

        if self.verbose:
            print("OK")

    def parse_first_hdr(self):
        if self.verbose:
            print("parsing first hdr..")
        self.read()

        pos = 0
        sign = read_uint(self.data, pos)
        if sign == HDR_T_SIGN:
            ch = HDR_T(self.data, pos)
            pos += ch.size
            self.chunks.append(ch)
        else:
            print("ERROR")

        if self.verbose:
            print("OK")

    def dump(self):
        print("%s Size: %s" % (os.path.basename(self.filename), sizeof_fmt(self.size)))


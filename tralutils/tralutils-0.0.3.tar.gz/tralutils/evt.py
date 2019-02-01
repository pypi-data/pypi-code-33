# -*- coding: utf-8 -*-

__author__ = 'sv99'


class EvtFile:
    def __init__(self, path, verbose=False):
        self.filename = path
        self._readed = False
        self._parsed = False
        self.data = None
        self.verbose = verbose

    @property
    def parsed(self):
        return self._parsed

    def parse(self):
        if self.verbose:
            print("parsing..")

        with open(self.filename, 'rb') as fp:

            self.data = bytearray(fp.read())

        self._parsed = True
        if self.verbose:
            print("OK")

    def dump(self):
        print("dump OK")
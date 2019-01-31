import sys
import os
import errno

from io import StringIO as StringIO
import re
import os.path
from types import ModuleType
import stat
import tarfile


def nonblank_lines(f):
    for l in f:
        line = l.rstrip()
        if line:
            yield line

'''
Container w/ loading/dumping capabilities for tsv formated text-file
'''
class Wrapper(object):
    def __init__(self, stream, ofs='\t', Nskip=0, dataParser=None, headerParser=None):
        self.ofs = ofs
        self.keymap = []
        self.data = []
        self.Nskip = Nskip
        self.dataParser = dataParser
        self.headerParser = headerParser


        if hasattr(stream, 'read'):
            self._loadStream(stream)
        elif isinstance(stream, basestring):
            if os.path.isfile(stream):
                self._loadFile(stream)
            else :
                self._loadString(stream)
        elif isinstance(stream, list):
            self._loadList(stream)
        else:
            raise TypeError('Cant parse/load ' + str(stream) )

    def _loadStream(self, stream):
        for i in range(self.Nskip):
            stream.readline()
        if self.headerParser:
            self.keymap = self.headerParser(stream.readline().replace("\n", ""))
        else:
            self.keymap = stream.readline().replace("\n", "").split(self.ofs)

        if self.dataParser:
            self.data = [ self.dataParser(l) for l in nonblank_lines(stream) ]
        else:
            self.data = [ self._push(l) for l in nonblank_lines(stream) ]



    def _loadList(self, inputList):

        if self.headerParser:
            self.keymap = self.headerParser( inputList[self.Nskip].replace("\n", "") )
        else :
            self.keymap = inputList[self.Nskip].replace("\n", "").split(self.ofs)

        if self.dataParser:
            self.data = [ self.dataParser(l) for l in nonblank_lines(inputList[ (self.Nskip+1): ])]
        else :
            self.data = [ self._push(l) for l in nonblank_lines(inputList[ (self.Nskip+1): ])]


    def _loadFile(self, fPath):
        with open(fPath, 'r') as stream:
            self._loadStream(stream)

    def _loadString(self, inputRaw):
        l = inputRaw.split('\n')
        self._loadList(l)


    def __len__(self):
        return len(self.data)

    def _push(self, inputRaw):
        #print ">" + self.ofs+ "<"
        #print inputRaw
        d = { self.keymap[i] : val for i, val in enumerate( inputRaw.split(self.ofs) ) }
        return d

    def __iter__(self):
        for d in self.data:
            yield d

    def __str__(self):
        asString= ''
        for i,value in enumerate(self.data):
            asString += '# Element n_' + str(i) + '\n'
            for k in self.keymap:
                if k not in value:
                    continue
                asString += '\'' + k + '\' : ' + value[ k ] + '\n'
        return asString

    def write(self):
        asString= '\t'.join(self.keymap) + '\n'
        for d in self :
            buf = [ d[ k ] for k in self.keymap ]
            asString += '\t'.join(buf) + '\n'
        return asString

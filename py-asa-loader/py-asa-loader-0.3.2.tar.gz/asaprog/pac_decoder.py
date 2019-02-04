from asaprog.util import *
import enum

class Status(enum.IntEnum):
    HEADER = 0
    COMMAND = 1
    TOCKEN = 2
    LENGTH = 3
    DATA = 4
    CHKSUM = 5

class PacketDecoder(object):
    _status = Status(Status.HEADER)
    _header_buffer = b'\x00\x00\x00'
    _counter = int()
    _command = int()
    _length  = int()
    _data    = bytes()
    _chksum  = int()
    _isError = bool()
    _isDone  = bool()

    def __init__(self):
        super(PacketDecoder, self).__init__()

    def step(self, ch):
        if self._status is Status.HEADER:
            self._header_buffer = self._header_buffer[1:3] + bytes([ch])
            if self._header_buffer == HEADER:
                self._chksum = 0
                self._status = Status.COMMAND
        elif self._status is Status.COMMAND:
            self._command = asaProgCommand(ch)
            self._counter = 0
            self._status = Status.TOCKEN
        elif self._status is Status.TOCKEN:
            self._status = Status.LENGTH
        elif self._status is Status.LENGTH:
            self._counter = self._counter + 1
            if self._counter == 1:
                self._length = ch << 8
            elif self._counter == 2:
                self._length += ch
                self._counter = 0
                self._data    = b''
                if self._length == 0:
                    self._status = Status.CHKSUM
                else:
                    self._status = Status.DATA
        elif self._status is Status.DATA:
            self._chksum += ch
            self._counter = self._counter + 1
            self._data += bytes([ch])
            if self._counter == self._length:
                self._status = Status.CHKSUM
        elif self._status is Status.CHKSUM:
            if self._chksum % 256 != ch:
                self._error = True
            self._status = Status.HEADER
            self._header_buffer = b'\x00\x00\x00'
            self._isDone = True
    
    def isDone(self):
        return self._isDone
    
    def isError(self):
        return self._isError
    
    def getPacket(self):
        if self.isDone():
            res = {
                'command': self._command,
                'data': self._data
            }
            self._isDone = False
            return res
        else:
            return None



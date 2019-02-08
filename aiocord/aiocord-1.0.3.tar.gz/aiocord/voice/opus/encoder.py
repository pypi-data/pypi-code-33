import os
import sys
import array
import ctypes
import ctypes.util

from . import errors


__all__ = ('Encoder',)


c_int_ptr = ctypes.POINTER(ctypes.c_int)

c_int16_ptr = ctypes.POINTER(ctypes.c_int16)

c_float_ptr = ctypes.POINTER(ctypes.c_float)


class EncoderStruct(ctypes.Structure):

    __slots__ = ()


EncoderStructPtr = ctypes.POINTER(EncoderStruct)


functions = (
    (
        'opus_strerror',
        (
            ctypes.c_int,
        ),
        ctypes.c_char_p
    ),
    (
        'opus_encoder_get_size',
        (
            ctypes.c_int,
        ),
        ctypes.c_int
    ),
    (
        'opus_encoder_create',
        (
            ctypes.c_int,
            ctypes.c_int,
            ctypes.c_int,
            c_int_ptr
        ),
        EncoderStructPtr
    ),
    (
        'opus_encode',
        (
            EncoderStructPtr,
            c_int16_ptr,
            ctypes.c_int,
            ctypes.c_char_p,
            ctypes.c_int32
        ),
        ctypes.c_int32
    ),
    (
        'opus_encoder_ctl',
        None,
        ctypes.c_int32
    ),
    (
        'opus_encoder_destroy',
        (EncoderStructPtr,),
        None
    )
)


def load():

    filename = ctypes.util.find_library('opus')

    lib = ctypes.cdll.LoadLibrary(filename)

    for name, argtypes, restype in functions:

        func = getattr(lib, name)

        if argtypes:

            func.argtypes = argtypes

        func.restype = restype

    return lib


class Application:

    AUDIO = 2049


class Control:

    BITRATE = 4002
    BANDWIDTH = 4008
    FEC = 4012
    PLP = 4014


class Encoder:

    lib = None

    __all__= ('state',)

    def __init__(self, rate, channels):

        if not self.lib:

            self.lib = load()

        self.state = None

        self.create(rate, channels, Application.AUDIO)

        self.bitrate(128)

        self.fec(True)

        self.expected_packet_loss(0.15)

    def create(self, rate, channels, audio):

        ret = ctypes.c_int()

        ret_ref = ctypes.byref(ret)

        result = self.lib.opus_encoder_create(rate, channels, audio, ret_ref)

        if not ret.value == 0:

            raise errors.Error('could not create state')

        self.state = result

    def bitrate(self, kbps):

        kbps = min(128, max(16, int(kbps)))

        mbps = kbps * 1024

        result = self.lib.opus_encoder_ctl(self.state, Control.BITRATE, mbps)

        if result:

            raise errors.Error('failed setting bitrate')

    def fec(self, value):

        result = self.lib.opus_encoder_ctl(self.state, Control.FEC, value)

        if result:

            raise errors.Error('failed setting fec')

    def expected_packet_loss(self, value):

        value = min(100, max(0, int(value * 100)))

        result = self.lib.opus_encoder_ctl(self.state, Control.PLP, value)

        if result:

            raise errors.Error('failed setting plp')

    def encode(self, pcm, size):

        max_bytes = len(pcm)

        pcm = ctypes.cast(pcm, c_int16_ptr)

        data = (ctypes.c_char * max_bytes)()

        result = self.lib.opus_encode(self.state, pcm, size, data, max_bytes)

        if result < 0:

            raise errors.Error('failed encoding')

        data = data[:result]

        return array.array('b', data).tobytes()

    def __del__(self):

        if self.lib and self.state:

            self.lib.opus_encoder_destroy(self.state)

        self.state = None

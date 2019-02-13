from abc import ABC, abstractmethod

import numpy as np

from .checks import is_binary_message
from .messages import pack_to_dec


class Modulator(ABC):
    """Abstract modulator class"""
    def __init__(self, *args, **kwargs): pass

    @abstractmethod
    def modulate_symbols(self, messages): pass


class IdentityModulator(Modulator):
    @staticmethod
    def modulate_symbols(messages):
        return messages

    @staticmethod
    def demodulate_symbols(messages):
        return messages


class BpskModulator(Modulator):
    @staticmethod
    def modulate_symbols(messages):
        if not is_binary_message(messages):
            raise ValueError("Only binary messages can be modulated.")
        messages = np.array(messages)
        mod_bits = 2*messages - 1  # maps: 0 --> -1 and 1 --> 1
        return mod_bits

class QamModulator(Modulator):
    @staticmethod
    def modulate_symbols(messages, m=4):
        """Modulate binary messages or codewords with QAM.

        Parameters
        ----------
        messages : array
            Array of messages or codewords that should be modulated. Every row 
            corresponds to one individual message. The number of columns is the
            length of the codewords and has to be an integer multiple of `m`.

        m : int, optional
            Modulation order. It has to be a square of a power of two.
        
        Returns
        -------
        symbols : array
            Array of modulated symbols. The number of rows is the same as in 
            `messages`. The number of rows is divided by `m`.
        """
        c = np.sqrt(m)
        if not (c == int(c) and np.log2(c) == int(np.log2(c))):
            raise ValueError("The modulation order needs to be a square of a "
                             "power of 2.")
        messages = np.array(messages)
        _bit_size_split = np.shape(messages)[1]/np.log2(m)
        if _bit_size_split != int(_bit_size_split):
            raise ValueError("The number of columns needs to be an integer "
                             "power of m.")
        _parts = np.split(messages, _bit_size_split, axis=1)
        _mod_parts = []
        for _part in _parts:
            _messages = pack_to_dec(_part)
            real = 2 * np.floor_divide(_messages, c) - c + 1
            imag = -2 * np.mod(_messages, c) + c - 1
            _mod_parts.append(real + 1j*imag)
        return np.hstack(_mod_parts)

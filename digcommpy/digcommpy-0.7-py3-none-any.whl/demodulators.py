from abc import ABC, abstractmethod

import numpy as np

from .checks import is_binary_message
from .messages import generate_data
from .modulators import QamModulator


class Demodulator(ABC):
    """Abstract modulator class"""
    def __init__(self, *args, **kwargs): pass

    @abstractmethod
    def demodulate_symbols(self, messages): pass


class IdentityDemodulator(Demodulator):
    @staticmethod
    def demodulate_symbols(messages):
        messages = np.array(messages)
        return messages


class BpskDemodulator(Demodulator):
    @staticmethod
    def demodulate_symbols(messages):
        messages = np.array(messages)
        idx = messages > 0
        messages[idx] = 1
        messages[~idx] = 0
        return messages

class QamDemodulator(Demodulator):
    @staticmethod
    def demodulate_symbols(messages, m=4):
        c = np.sqrt(m)
        if not (c == int(c) and np.log2(c) == int(np.log2(c))):
            raise ValueError("The modulation order needs to be a square of a "
                             "power of 2.")
        messages = np.array(messages)
        all_messages = generate_data(np.log2(m), number=None, binary=True)
        all_mod_symbols = QamModulator.modulate_symbols(all_messages, m)
        all_mod_symbols = np.ravel(all_mod_symbols)
        _messages = np.tile(messages, (len(all_mod_symbols), 1, 1))
        _all_mod_symbols = np.tile(all_mod_symbols, (1, 1, 1)).reshape((-1, 1, 1))
        distances = np.abs(_messages - _all_mod_symbols)
        _idx_min = np.argmin(distances, axis=0)
        demod_symbols = all_messages[_idx_min]
        demod_symbols = np.hstack(np.dstack(demod_symbols.T))
        return demod_symbols

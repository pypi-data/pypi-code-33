from abc import ABC, abstractmethod

import numpy as np

from .checks import is_binary_message
from . import information_theory as it


class Channel(ABC):
    """Abstract channel class."""
    @abstractmethod
    def transmit_data(self, messages): pass

    @abstractmethod
    def capacity(): pass

    @abstractmethod
    def set_params(self, new_params): pass


class BinaryInputChannel(Channel, ABC):
    """Abstract channel class for binary input channels"""
    @abstractmethod
    def transmit_data(self, messages):
        if not is_binary_message(messages):
            raise TypeError("Messages for binary input channels have to be "
                            "binary (only 0 and 1).")


class AwgnChannel(Channel):
    """Additive white Gaussian noise channel.
    
    Parameters
    ----------
    snr_db : float
        Signal-to-noise ratio in dB.

    rate : float, optional
        Rate of the information bits to transmitted symbols (includes code and
        modulation rate)

    input_power : float, optional
        Input power of the symbols. If None, the power is estimated.
    """
    def __init__(self, snr_db, rate=1., input_power=None):
        self.snr_db = snr_db
        if 0 < rate <= 1.:
            self.rate = rate
        else:
            raise ValueError("The rate has to be in (0, 1]")
        self.input_power = input_power
        if input_power is not None:
            snr_lin = 10**(snr_db/10.)
            self.noise_var = input_power/(2.*rate*snr_lin)

    def transmit_data(self, messages):
        return self._awgn(messages, self.snr_db, self.rate, self.input_power)

    @staticmethod
    def _awgn(messages, snr=0., rate=1., input_power=None):
        """Additive White Gaussian Noise channel.

        Parameters
        ----------
        messages : array
            Array of shape (num_messages, num_uses) which holds the channel inputs.

        snr : float, optional
            Signal-to-noise-ratio in dB.

        rate : float, optional
            Float between [0, 1] which indicates the coding and modulation rate.

        input_power : float, optional
            Specify the input power. If `None`, the power is estimated as variance
            of the messages.

        Returns
        -------
        output : array
            Channel output with the same dimensions as the input.
        """
        if input_power is None:
            #input_power = np.mean(np.var(messages, axis=1))
            input_power = np.var(messages)
        snr_lin = 10**(snr/10.)
        noise_power = input_power/(2.*rate*snr_lin)
        noise = np.random.normal(loc=0, scale=np.sqrt(noise_power),
                                 size=np.shape(messages))
        output = messages + noise
        return output

    def capacity(self):
        capacity = np.log2(1.+self.snr_db)
        return capacity

    def set_params(self, snr_db):
        self.snr_db = snr_db


class BawgnChannel(AwgnChannel):
    def capacity(self):
        capacity = it._capacity_bawgn(self.snr_db)
        return capacity


class BecChannel(BinaryInputChannel):
    """Binary erasure channel."""
    def __init__(self, epsilon):
        if 0 <= epsilon <= 1:
            self.epsilon = epsilon
        else:
            raise ValueError("Erasure probability needs to be in [0, 1].")

    def transmit_data(self, messages):
        super().transmit_data(messages)
        return self._bec(messages, self.epsilon)

    @staticmethod
    def _bec(messages, epsilon):
        """Binary erasure channel.

        Binary messages will be mapped to (0, 1, -1) where -1 denotes the erasure
        symbol.

        Parameters
        ----------
        messages : array
            Array of shape (num_messages, num_uses) which holds the channel inputs.

        epsilon : float
            Erasure probability (channel parameters)

        Returns
        -------
        output: array
            Channel output with the same dimensions as the input. -1 denotes the
            erasure symbol.
        """
        idx_noise = np.random.choice([True, False], p=[epsilon, 1.-epsilon],
                                     size=np.shape(messages))
        output = np.array(messages)
        output[idx_noise] = -1
        return output

    def capacity(self):
        return 1.-self.epsilon

    def set_params(self, epsilon):
        self.epsilon = epsilon


class BscChannel(BinaryInputChannel):
    """Binary symmetric channel"""
    def __init__(self, prob):
        if 0 <= prob <= 1:
            self.prob = prob
        else:
            raise ValueError("Bit flip probability needs to be in [0, 1].")

    def transmit_data(self, messages):
        super().transmit_data(messages)
        return self._bsc(messages, self.prob)

    @staticmethod
    def _bsc(messages, prob):
        flips = np.random.choice([1, 0], p=[prob, 1.-prob],
                                 size=np.shape(messages))
        output = np.array(messages) + flips
        output = np.mod(output, 2)
        return output

    def capacity(self):
        return 1.-it.binary_entropy(self.prob)

    def set_params(self, prob):
        if 0 <= prob <= 1:
            self.prob = prob
        else:
            raise ValueError("Bit flip probability needs to be in [0, 1].")

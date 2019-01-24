'''
Parent class for noise models.

MAGIC
@author: Isobel
'''
from copy import deepcopy
import abc


class NoiseParent(object):
    __metaclass__ = abc.ABCMeta

    @abc.abstractmethod
    def __init__(self, ifo, verbose=False):
        # Set up a pointer to the interferometer class
        self.ifo = ifo
        self.verbose = verbose
        if self.verbose:
            print('Setting up ' + self.__class__.__name__)

    @abc.abstractmethod
    def getNoise(self):
        raise NotImplementedError('Undefined getNoise function')

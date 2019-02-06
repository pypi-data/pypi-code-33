
from .AbstractNormalizer import AbstractNormalizer
import numpy as np
import scipy.stats.mstats as st


class OutlierNormalizer(AbstractNormalizer):

    def __init__(self, positive_required):
        super().__init__()
        self.__positive_required = positive_required

    def normalize(self, matrix, verbose=False):

        if verbose:
            print("Performing outlier normalization")

        return matrix.array


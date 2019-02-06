
from .AbstractNormalizer import AbstractNormalizer
import numpy as np
import scipy.stats.mstats as st

class WinsorizationNormalizer(AbstractNormalizer):

    def __init__(self, positive_required, limits=0.05):
        super().__init__()
        self.__positive_required = positive_required
        self.__limits = limits

    def normalize(self, matrix, verbose=False):

        if verbose:
            print("Performing Winsorization")

        array = matrix.array
        result = []

        for row in array:
            result.append(st.winsorize(row, limits=self.__limits))

        return array


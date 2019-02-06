
from .AbstractNormalizer import AbstractNormalizer
import numpy as np


class StandardNormalizer(AbstractNormalizer):

    def __init__(self, positive_required):
        super().__init__()
        self.__positive_required = positive_required

    def normalize(self, matrix, verbose=False):

        if verbose:
            print("Performing standard normalization")

        abs_min_value = abs(matrix.array.min(axis=0))

        if self.__positive_required:
            processed_array = matrix.array + abs_min_value
        else:
            processed_array = matrix.array

        abs_max_value = abs(processed_array.max(axis=0))
        abs_min_value = abs(processed_array.min(axis=0))

        division_factor = []

        for index in range(len(abs_max_value)):
            division_factor.append(max(abs_max_value[index],
                                       abs_min_value[index]))

        return processed_array / np.array(division_factor)

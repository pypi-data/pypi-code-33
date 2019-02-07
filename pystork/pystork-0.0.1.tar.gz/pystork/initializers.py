from abc import ABC, abstractmethod
from typing import Union
import numpy as np


class AbstractInitializer(ABC):
    @abstractmethod
    def get_values(self, x_dim: int, y_dim: int) -> Union[np.array, float]:
        """
        :param x_dim:
        :param y_dim:
        :return: a vector of dimensions (x_dim, y_dim)
        """


class RandomInitializer(AbstractInitializer):
    def __init__(self, reduction: float = 0.01):
        """
        :param reduction: a very small float used to make very small initializations in order
        to make convergence easier
        """
        self.reduction = reduction

    def get_values(self, x_dim: int, y_dim: int) -> np.array:

        return np.random.randn(x_dim, y_dim)


class ZerosInitializer(AbstractInitializer):
    def get_values(self, x_dim: int, y_dim: int) -> np.array:
        initialization = np.zeros((x_dim, y_dim))

        return initialization

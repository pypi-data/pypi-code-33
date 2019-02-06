
from .AbstractReconstructor import AbstractReconstructor

import numpy.linalg as la
import numpy as np
from copy import deepcopy


class SingleMatrixReconstructor(AbstractReconstructor):

    def __init__(self):
        super().__init__()

    def reconstruct(self, eigenvectors, eigenvalues):
        return (eigenvectors @ np.diag(eigenvalues) @ la.inv(eigenvectors)).real

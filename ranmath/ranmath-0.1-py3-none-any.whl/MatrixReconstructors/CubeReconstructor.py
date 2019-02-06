from .AbstractReconstructor import AbstractReconstructor

import numpy.linalg as la
import numpy as np


class CubeReconstructor(AbstractReconstructor):

    def __init__(self):
        super().__init__()

    def reconstruct(self, cube_eigenvectors, cube_eigenvalues):
        result = []
        for i in range(len(cube_eigenvectors)):
            result.append((cube_eigenvectors[i] @ np.diag(cube_eigenvalues[i]) @ la.inv(cube_eigenvectors[i])).real)
        return np.array(result)

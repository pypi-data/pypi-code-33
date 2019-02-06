
import numpy as np
import pandas as pd
from weakref import ReferenceType


class MatrixImporter:

    def __init__(self, matrix_reference: ReferenceType):
        self.matrix_reference = matrix_reference

    def from_CSV(self, filepath: str):
        print("Importing from CSV:", filepath)
        self.matrix_reference().array = np.array([pd.read_csv(filepath, header=None).values.T])

    def from_ndarray(self, array: np.ndarray):
        print("Importing from NDArray")
        self.matrix_reference().array = array

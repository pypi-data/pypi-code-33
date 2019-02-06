
import numpy as np
import pandas as pd
from weakref import ReferenceType


class MatrixExporter:

    def __init__(self, matrix_reference: ReferenceType):
        self.matrix_reference = matrix_reference

    def to_CSV(self, filepath: str):
        print("Exporting to CSV:", filepath)
        pd.DataFrame(self.matrix_reference().array[0].T).to_csv(filepath, header=None, index=None)

    def to_ndarray(self) -> np.ndarray:
        print("Exporting to NDArray")
        return self.matrix_reference().array
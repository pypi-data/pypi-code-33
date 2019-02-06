
import weakref
import numpy as np

from .MatrixGenerators import MatrixGeneratorAdapter
from .MatrixNormalizers import MatrixNormalizerAdapter
from .MatrixSamplers import MatrixSamplerAdapter
from .MatrixDataManagement.MatrixExporter import MatrixExporter
from .MatrixDataManagement.MatrixImporter import MatrixImporter


class TimeSeriesMatrix:

    def __init__(self):
        self.generate = MatrixGeneratorAdapter(weakref.ref(self))
        self.normalize = MatrixNormalizerAdapter(weakref.ref(self))
        self.characteristics = MatrixSamplerAdapter(weakref.ref(self))
        self.import_matrix = MatrixImporter(weakref.ref(self))
        self.export_matrix = MatrixExporter(weakref.ref(self))
        self._array = None

    @property
    def array(self) -> np.ndarray:
        return self._array

    @array.setter
    def array(self, value: np.ndarray):
        self._array = value



# -------------------------------------------------------------------------------------------------
# Quantum Feature Detector
# Copyright 2018 QxBranch, Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
# To learn more about QxBranch, see <https://www.qxbranch.com>.
# -------------------------------------------------------------------------------------------------

from abc import abstractmethod
from typing import Any, Generic, Sequence, Tuple, TypeVar, Type

from qxbranch.quantum_feature_detector.encoder_base import EncoderBase
from qxbranch.quantum_feature_detector.decoder_base import TDecodedResults, DecoderBase
from qxbranch.quantum_feature_detector.quantum_transform import QuantumTransform
from qxbranch.quantum_feature_detector import logging_service

TCircuit = TypeVar('TCircuit', bound='Circuit')
TEncoder = TypeVar('TEncoder', bound=EncoderBase)
TDecoder = TypeVar('TDecoder', bound=DecoderBase)
TMeasurementResults = TypeVar('TMeasurementResults')


class Circuit(Generic[TCircuit, TEncoder, TDecoder, TMeasurementResults]):
    """
    A general class for building and running quantum programs from circuits defined by
    :py:class:`QuantumTransform` objects.

    :param quantum_transforms: The quantum transforms that define the circuit this class encapsulates. Sequence of
        application is implied by the order of the transformations in the tuple.
    """

    def __init__(self, quantum_transforms: Tuple[QuantumTransform, ...]) -> None:
        self._logger = logging_service.get_logger(self.__class__.__name__)
        self._transforms = quantum_transforms
        self._qubit_count = max([max(transform.qubit_indices) for transform in self._transforms]) + 1

    @classmethod
    def from_dict(cls: Type[TCircuit], circuit_dict: dict) -> TCircuit:
        """Builds a :py:class:`circuit.Circuit` from a `dict`."""
        transforms = [QuantumTransform.from_dict(transform_dict) for transform_dict in circuit_dict['transforms']]
        return cls(tuple(transforms))

    def to_dict(self) -> dict:
        """Writes out this :py:class:`circuit.Circuit` to a JSON-writable `dict`."""
        return {'transforms': [transform.to_dict() for transform in self._transforms]}

    @abstractmethod
    def run_program(self, input_data: Sequence[Any], encoder: TEncoder, decoder: TDecoder) -> TDecodedResults:
        """This method needs to be implemented for each derived subclass."""
        raise NotImplementedError('Please implement this method')

    @property
    def transforms(self) -> Tuple[QuantumTransform, ...]:
        """The QuantumTransforms that define the circuit this class encapsulates. Order implies sequence."""
        return self._transforms

    @property
    def qubit_count(self) -> int:
        """The number of qubits in this circuit."""
        return self._qubit_count

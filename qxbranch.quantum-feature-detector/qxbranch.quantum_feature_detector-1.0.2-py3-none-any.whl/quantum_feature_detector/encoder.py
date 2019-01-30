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
from typing import Any, Generic, List, Sequence, TypeVar

from qxbranch.quantum_feature_detector import logging_service

TEncodedQubits = TypeVar('TEncodedQubits')


class Encoder(Generic[TEncodedQubits]):
    """
    Generic encoder object for inheriting. Encoders are used to take classical data and turn it into something a quantum
    circuit can use.
    """

    def __init__(self, qubit_count: int) -> None:
        self._qubit_count = qubit_count
        self._logger = logging_service.get_logger(self.__class__.__name__)

    @abstractmethod
    def encode_qubits(self, input_data: Sequence[Any], available_qubits: List[int]) -> TEncodedQubits:
        """Method for encoding a vector of classical data into a quantum circuit."""
        raise NotImplementedError('Please implement this method')

    @property
    def qubit_count(self) -> int:
        """Number of qubits this encoder uses."""
        return self._qubit_count

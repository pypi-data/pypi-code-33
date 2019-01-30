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

from typing import Tuple, Optional

from qxbranch.quantum_feature_detector import logging_service


class QuantumTransform:
    """
    A class that described quantum transformations in a JSON-writable format.

    :param gate: The name of the gate used in the transformation.
    :param qubit_indices: The indices of the qubits the transform is applied to. In the case of controlled gates,
        control qubits should come before target qubits.
    :param radians: Optional phase shift rotation parameter for gates that require it. Defaults to None.
    """

    def __init__(self, gate: str, qubit_indices: Tuple[int, ...], radians: Optional[float] = None) -> None:
        self._logger = logging_service.get_logger(self.__class__.__name__)
        self._gate = gate
        self._qubit_indices = qubit_indices
        self._radians = radians

    @property
    def gate(self) -> str:
        """The name of the encoded gate."""
        return self._gate

    @property
    def qubit_indices(self) -> Tuple[int, ...]:
        """The indices of the target qubits. In the case of controlled gates, controls are first."""
        return self._qubit_indices

    @property
    def radians(self) -> Optional[float]:
        """The radians parameter for phase shift gates."""
        return self._radians

    @staticmethod
    def from_dict(transform_dict: dict) -> 'QuantumTransform':
        """Builds a :py:class:`QuantumTransform` from a `dict`."""
        return QuantumTransform(**transform_dict)

    def to_dict(self) -> dict:
        """Writes the :py:class:`QuantumTransform` to a `dict`."""
        return {'gate': self.gate,
                'qubit_indices': self.qubit_indices,
                'radians': self.radians}

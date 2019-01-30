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

from typing import Sequence, Tuple

from third_party.quantum_circuit_diagram_plotter.qcircuit import QCircuit, Gate

from qxbranch.quantum_feature_detector.circuit_base import CircuitBase, TEncoder, TDecoder
from qxbranch.quantum_feature_detector.quantum_transform import QuantumTransform


class PlottableCircuit(CircuitBase['PlottableCircuit', TEncoder, TDecoder, QCircuit]):
    def __init__(self, quantum_transforms: Tuple[QuantumTransform]) -> None:
        """
        Class for drawing circuit diagrams.
        """
        super(PlottableCircuit, self).__init__(quantum_transforms=quantum_transforms)

    def run_program(self, input_data: Sequence[int] = None, encoder: TEncoder = None, decoder: TDecoder = None) -> QCircuit:
        """
        Draws a diagram of the circuit.
        """
        self._logger.debug("Plotting circuit.")

        circuit_diagram = QCircuit()
        qubits = circuit_diagram.zeros(ls=['q{}'.format(idx) for idx in range(self.qubit_count)])

        """Internal method, builds out a pyquil Program from a list of QuantumTransforms"""
        for transform in self.transforms:
            gate = transform.gate
            if transform.radians is not None:
                Gate(gate)(*[qubits[idx] for idx in transform.qubit_indices])
            else:
                Gate('{}({})'.format(gate, transform.radians))(*[qubits[idx] for idx in transform.qubit_indices])
        return circuit_diagram

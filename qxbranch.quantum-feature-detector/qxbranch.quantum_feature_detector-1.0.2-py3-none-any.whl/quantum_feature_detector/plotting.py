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

from typing import Sequence

from qxbranch.quantum_feature_detector.quantum_model import QuantumModel
from qxbranch.quantum_feature_detector.circuit_base import TCircuit, TEncoder
from qxbranch.quantum_feature_detector.plottable_circuit import PlottableCircuit


def plot_quantum_transformed_data(input_data: Sequence[int], quantum_model: QuantumModel) -> Sequence[int]:
    """
    Applies the transforms from a model's QFDs to a sequence of input data, then restructures that data to match
    the shape of the input data by taking the mean value of the output of all QFDs applied to each data point.

    :param input_data: The vector of input data to transform.
    :param quantum_model: The model containing the QFDs to apply.
    :return: A vector of quantum-transformed data in the same shape as the input.
    """
    transformed_data = quantum_model.apply_qfds_to_data(input_data)
    plottable_data = []
    for quantum_output in transformed_data:
        mean_data = sum(quantum_output) / len(quantum_output)
        plottable_data.append(mean_data)
    return plottable_data


def plot_circuit_diagram(circuit: TCircuit, encoder: TEncoder):
    """
    Builds a quantum circuit diagram from any Circuit subclass.

    :param circuit: A quantum circuit implementing Circuit as its superclass.
    :return: A pyplot containing a diagram of the quantum circuit.
    """
    plottable_circuit = PlottableCircuit(quantum_transforms=circuit.transforms, qubit_count=circuit.qubit_count)
    plot = plottable_circuit.run_program(encoder=encoder)
    return plot

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

import random
from typing import Optional, Tuple, Union

from pyquil.api import QuantumComputer

from qxbranch.quantum_feature_detector.pyquil.circuit import Circuit
from qxbranch.quantum_feature_detector.quantum_transform import QuantumTransform
from qxbranch.quantum_feature_detector.circuit_generator_base import CircuitGeneratorBase


class CircuitGenerator(CircuitGeneratorBase[Union[QuantumComputer, str], Circuit]):
    """
    Factory class for generating random :py:class:`Circuit` objects for
    use in :py:class:`QuantumFeatureDetector` objects.

    :Example:
        Create a factory for generating :py:class:`Circuit` objects, each with 5 qubits and 8
        gates, and generate 5 such circuits.

        >>> circuit_generator = CircuitGenerator(qubit_count=5, gate_count=8)
        >>> circuit_pyquils = circuit_generator.generate_multiple(circuit_count=5)

        Create a factory as above, but restricted to only use Pauli-X and CNot gates.

        >>> circuit_generator = CircuitGenerator(qubit_count=5, gate_count=8,
        ...                                            one_qubit_gate_types=('X', ),
        ...                                            two_qubit_gate_types=('CNOT', ))

        Create a factory as above, but using a random instance to seed circuit generation.

        >>> circuit_generator = CircuitGenerator(qubit_count=5, gate_count=8,
        ...                                            random_instance=random.Random(1))

        Create a factory as above, but using a different quantum backend, and 10 trials at runtime.

        >>> circuit_generator = CircuitGenerator(qubit_count=5, gate_count=8,
        ...                                            backend='Aspen-0-5Q-C',
        ...                                            number_of_runs=10)

    :param qubit_count: The number of qubits in the generated circuits.
    :param gate_count: The number of gates in the generated circuits. Must be greater than the qubit count, so that all
        qubits in the circuit can be connected.
    :param backend: The quantum backend the circuit should be executed on. Must be a
        :py:class:`pyquil.api.QuantumComputer`, or a `str` compatible with the :py:meth:`pyquil.api.get_qc` method.
        Defaults to the quantum virtual machine returned by :py:class:`pyquil.api.QVMConnection`.
    :param one_qubit_gate_types: A tuple of strings that defines the names of allowable one-qubit gates when generating
        the random circuit. Defaults to ('X', 'Y', 'Z', 'H', 'S', 'T', 'RX', 'RY', 'RZ').
    :param two_qubit_gate_types: A tuple of strings that defines the names of allowable two-qubit gates when generating
        the random circuit. Defaults to ('CZ', 'CNOT').
    :param edge_probability: Optional probability used to determine how often edges should appear in the graph used to
        generate circuits. Note that graphs must always be connected, so low probabilities may lead to long run-times as
        the generator tries to find a connected graph. Defaults to 0.4.
    :param number_of_runs: Number of times generated circuits will be executed at runtime. Defaults to 1.
    :param backend_seed: Value used to seed the quantum backend at runtime. Defaults to 1, but `None` should be used to
        randomly generate a seed. Note that not all quantum backends support use of a seed.
    :param random_instance: An optional random state used to seed all circuit generation.
    """

    def __init__(self, qubit_count: int, gate_count: int,
                 backend: Optional[Union[str, QuantumComputer]] = None,
                 one_qubit_gate_types: Tuple[str, ...] = ('X', 'Y', 'Z', 'H', 'S', 'T', 'RX', 'RY', 'RZ'),
                 two_qubit_gate_types: Tuple[str, ...] = ('CZ', 'CNOT'),
                 edge_probability: float = 0.4, number_of_runs: int = 1, backend_seed: int = 1,
                 random_instance: Optional[random.Random] = None) -> None:
        super(CircuitGenerator, self).__init__(qubit_count=qubit_count, gate_count=gate_count, backend=backend,
                                               one_qubit_gate_types=one_qubit_gate_types,
                                               two_qubit_gate_types=two_qubit_gate_types,
                                               edge_probability=edge_probability,
                                               random_instance=random_instance)
        self._number_of_runs = number_of_runs
        self._backend_seed = backend_seed

    def _generate_instance(self, random_circuit: Tuple[QuantumTransform, ...],
                           qubit_count: int) -> Circuit:
        return Circuit(quantum_transforms=random_circuit, backend=self.backend,
                       number_of_runs=self.number_of_runs, seed=self.backend_seed)

    @property
    def number_of_runs(self) -> int:
        """Number of times generated circuits will be executed at runtime."""
        return self._number_of_runs

    @property
    def backend_seed(self) -> int:
        """Value used to seed the quantum backend at runtime. Does not apply to all types of quantum backends."""
        return self._backend_seed

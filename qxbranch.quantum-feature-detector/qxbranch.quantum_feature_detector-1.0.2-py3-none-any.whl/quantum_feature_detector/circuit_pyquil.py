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

import time
from typing import Any, Iterable, List, Optional, Sequence, Tuple, Union

from pyquil.api import QuantumComputer, get_qc, QVMConnection
from pyquil.quil import Gate, Program
from pyquil import quilbase
import pyquil.gates

from qxbranch.quantum_feature_detector.pyquil.encoder import Encoder
from qxbranch.quantum_feature_detector.pyquil.decoder import Decoder, MeasurementResultsPyquil
from qxbranch.quantum_feature_detector.circuit_base import CircuitBase, TDecodedResults
from qxbranch.quantum_feature_detector.quantum_transform import QuantumTransform


class CircuitPyquil(CircuitBase['CircuitPyquil', Encoder, Decoder, MeasurementResultsPyquil]):
    """
    Class for building and running a :py:class:`Circuit` for the Forest environment.

    :Example:
        Create a `CircuitPyquil` that entangles two qubits as an EPR pair. First, using a pyquil Program:

        >>> quantum_program = pyquil.quil.Program()
        >>> quantum_program.inst(pyquil.gates.H(0))
        >>> quantum_program.inst(pyquil.gates.CNOT(0, 1))
        >>> epr_circuit = CircuitPyquil(quantum_transforms=quantum_program)

        And now using :py:class:`quantum_transform.QuantumTransform` objects:

        >>> transforms = (QuantumTransform(gate='H', qubit_indices=(0, )),
        ...               QuantumTransform(gate='CNOT', qubit_indices=(0, 1)))
        >>> epr_circuit = CircuitPyquil(quantum_transforms=transforms)

        And running on a specified hardware backend:

        >>> quantum_computer = pyquil.api.get_qc('Aspen-0-5Q-C')
        >>> epr_circuit = CircuitPyquil(quantum_transforms=transforms,
        ...                             backend=quantum_computer)

    :param quantum_transforms: Defines the circuit encapsulated by this class. Can be provided as either a `tuple` of
        :py:class:`quantum_transform.QuantumTransform` objects or a :py:class:`pyquil.quil.Program`.
    :param backend: The quantum backend the circuit should be executed on. Must be a
        :py:class:`pyquil.api.QuantumComputer`, or a `str` compatible with the :py:meth:`pyquil.api.get_qc` method.
        Defaults to the quantum virtual machine returned by :py:class:`pyquil.api.QVMConnection`.
    :param number_of_runs: Number of times the circuit should be executed by the backend at runtime. Defaults to 1.
    :param seed: Value used to seed the quantum backend at runtime. Defaults to 1, but `None` should be used to randomly
        generate a seed. Note that not all quantum backends support use of a seed.
    """

    def __init__(self, quantum_transforms: Union[Tuple[QuantumTransform, ...], Program],
                 backend: Optional[Union[str, QuantumComputer]] = None,
                 number_of_runs: int = 1, seed: int = 1) -> None:
        if backend is None:
            self._backend = QVMConnection(random_seed=seed)
        elif isinstance(backend, QuantumComputer):
            self._backend = backend
        elif isinstance(backend, str):
            self._backend = get_qc(backend)
        else:
            raise TypeError("Specified backend {} is invalid".format(backend))

        if isinstance(quantum_transforms, Program):
            quantum_transforms = self._program_to_transforms(quantum_transforms)
        elif not isinstance(quantum_transforms, tuple):
            raise TypeError(
                "quantum_transforms {} are invalid. Must be pyquil.quil.Program or tuple of QuantumTrasnforms".format(
                    quantum_transforms))

        self._number_of_runs = number_of_runs
        self._seed = seed

        super(CircuitPyquil, self).__init__(quantum_transforms=quantum_transforms)

        if isinstance(self._backend, QuantumComputer):
            if self.qubit_count > len(self._backend.qubits()):
                raise ValueError("Specified backend {} does not have the {} qubits required for this circuit".format(
                    self._backend, self.qubit_count))
            self._qubit_mappings = self._backend.qubits()
        else:
            self._qubit_mappings = [i for i in range(self.qubit_count)]

    def _create_circuit(self, quantum_program: Program) -> Program:
        """Internal method, builds out a pyquil Program from a list of QuantumTransforms"""
        for transform in self.transforms:
            qubit_indices = [self._qubit_mappings[qi] for qi in transform.qubit_indices]
            try:  # @TODO: Review that this is the best way to determine whether an arbitrary gate takes radians
                quantum_program.inst(getattr(pyquil.gates, transform.gate)(transform.radians, *qubit_indices))
            except TypeError:
                quantum_program.inst(getattr(pyquil.gates, transform.gate)(*qubit_indices))
        return quantum_program

    @staticmethod
    def _program_to_transforms(pyquil_program: Program) -> Tuple[QuantumTransform, ...]:
        """Internal method, converts a pyquil Program to a list of QuantumTransforms"""
        # This checks that the program only contains gates
        pyquil_instructions = pyquil_program.instructions
        quantum_transforms = []
        for gate in pyquil_instructions:
            if not isinstance(gate, Gate):
                raise TypeError("Pyquil circuits must be built from programs consisting of only gates. Invalid "
                                "instruction {}".format(gate))

            qubit_indices = tuple([quilbase._extract_qubit_index(qubit) for qubit in gate.qubits])

            if len(gate.params) >= 1:
                radians = gate.params[0]
            else:
                radians = None

            quantum_transforms.append(QuantumTransform(gate.name, qubit_indices, radians))
        return tuple(quantum_transforms)

    def run_program(self, input_data: Sequence[Any], encoder: Encoder,
                    decoder: Decoder) -> TDecodedResults:
        """
        Runs the circuit on the data vector provided, encoding the data to the circuit using the providing encoder, and
        decoding the circuit measurement results using the provided decoder.

        :param input_data: Vector defining the data for encoding into the circuit.
        :param encoder: Encoder wrapping a pyquil Program that encodes the data to the circuit.
        :param decoder: Decoder wrapping classical post-processing applied to the measurement results from the completed
            quantum circuit.
        :return: The results of executing the circuit.
        """
        self._logger.debug("Running circuit on backend: {}".format(self._backend))

        start_time = time.time()

        self._logger.debug("Encoding data: {}".format(input_data))

        self._logger.debug("Mapping circuit to available qubits: {}".format(self._qubit_mappings))
        quantum_program = encoder.encode_qubits(input_data=input_data, available_qubits=self._qubit_mappings)

        self._create_circuit(quantum_program=quantum_program)

        if isinstance(self._backend, QuantumComputer):
            measurement_results = self._backend.run_and_measure(quantum_program, trials=self._number_of_runs)
        elif isinstance(self._backend, QVMConnection):
            qvm_results = self._backend.run_and_measure(quantum_program, qubits=self._qubit_mappings,
                                                        trials=self._number_of_runs)
            measurement_results = CircuitPyquil._qvm_to_qc_results(qvm_results)
        else:
            raise ValueError('Backend {} is not a valid quantum backend.'.format(self._backend))

        self._logger.debug("Raw measurement results: {}".format(measurement_results))

        self._logger.debug("Trimming unused qubit values...")
        trimmed_results = {i: measurement_results[self._qubit_mappings[i]] for i in range(self.qubit_count)}

        decoded_result = decoder.decode_measurement(trimmed_results)
        self._logger.debug("Decoded results: {}".format(decoded_result))

        end_time = time.time()
        execution_time_seconds = end_time - start_time
        self._logger.debug("Circuit runtime: {}s".format(execution_time_seconds))

        return decoded_result

    @staticmethod
    def _qvm_to_qc_results(qvm_results: List[List[int]]) -> dict:
        """Converts output from a QVMConnection backend to the format output by a QuantumComputer backend"""
        while isinstance(qvm_results[0][0], Iterable):
            qvm_results = qvm_results[0]
        qc_results = {}
        for qubit_index in range(len(qvm_results[0])):
            qc_results[qubit_index] = [qvm_result[qubit_index] for qvm_result in qvm_results]
        return qc_results

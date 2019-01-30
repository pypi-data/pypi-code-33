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

import numpy as np
from typing import Any, List, Sequence

from pyquil.quil import Program
from pyquil.gates import RX, X

from qxbranch.quantum_feature_detector.encoder_base import EncoderBase


class EncoderPyquil(EncoderBase[Program]):
    """Generic encoder object compatible with :py:class:`CircuitPyquil` objects."""

    def __init__(self, qubit_count: int) -> None:
        super(EncoderPyquil, self).__init__(qubit_count)


class EncoderPyquilQuantumKitchenSinks(EncoderPyquil):
    """
    Encoder class for encoding input data to the circuit as the angle parameters in :py:class:`pyquil.gates.RX` gates.

    For a detailed explanation of how this encoder functions, refer to `Wilson et. al. 2018, Quantum Kitchen Sinks`_.

    .. _`Wilson et. al. 2018, Quantum Kitchen Sinks`: https://arxiv.org/pdf/1806.08321.pdf

    :Example:

        Create an encoder that takes data vectors of length 5 and encodes them to a 3-qubit circuit:

        >>> encoder = EncoderPyquilQuantumKitchenSinks(qubit_count=3, data_size=5,
        ...                                            non_zero_count=3)
        >>> quantum_transformed_data = circuit_pyquil.run_program(
        ...     input_data=test_data,
        ...     encoder=encoder,
        ...     decoder=DecoderPyquilMostCommon())


    :param qubit_count: The number of qubits in the circuits. :math:`q` in the Quantum Kitchen Sinks paper.
    :param data_size: The length of the input data vectors. :math:`p` in the Quantum Kitchen Sinks paper.
    :param non_zero_count: The number of non-zero entries in each row of the :math:`\\Omega` matrix, used to generate
        encodings for the data onto the quantum circuit. By default will randomly select a value for `non_zero_count`
        that is less than the `data_size`.
    :param sigma: Standard deviation of the normal distribution used to generate the non-zero values in :math:`\\Omega`.
    :param episode_number: Used to seed the generation of :math:`\\Omega` and :math:`\\beta` as per the Quantum Kitchen
        Sinks paper.
    """

    def __init__(self, qubit_count: int, data_size: int, non_zero_count: int = None, sigma: float = 1.0,
                 episode_number: int = 1) -> None:
        super(EncoderPyquilQuantumKitchenSinks, self).__init__(qubit_count=qubit_count)
        self._data_size = data_size
        self.__random_state = np.random.RandomState(seed=episode_number)

        # According to the QKS paper, use input_data and qubit_count to apply RX rotations to each qubit
        # Theta_i,e = Omega_e*U_i + Beta_e
        # self.qubit_count == q
        # self.data_size == p
        # non_zero_count == r

        omega = np.zeros((self.qubit_count, self.data_size))
        if non_zero_count is None:
            non_zero_count = self.__random_state.randint(1, self.data_size)
        omega_distribution = self.__random_state.normal(scale=sigma, size=(self.qubit_count, non_zero_count))

        for row in range(len(omega)):
            for index in range(len(omega_distribution[row])):
                for col in self.__random_state.choice(self.data_size, non_zero_count):
                    omega[row][col] = omega_distribution[row][index]

        self._omega = omega
        self._beta = self.__random_state.uniform(0, 2 * np.pi, size=(self.qubit_count,))

    def encode_qubits(self, input_data: Sequence[Any], available_qubits: List[int]) -> Program:
        """
        Encodes the given vector of data into a quantum circuit as X-rotations using :py:class:`pyquil.gates.RX` gates.

        :param input_data: The data to be encoded.
        :param available_qubits: List of qubits that are available on the quantum backend. Supports use of custom
            lattices.
        :return: Contains the :py:class:`pyquil.gates.RX` gates defined by the encoding methodology.
        """
        if len(input_data) != self.data_size:
            raise ValueError('input_data ({}) must be length {}.'.format(input_data, self.data_size))

        quantum_program = Program()

        # Theta_i,e = Omega_e*U_i + Beta_e
        rotation_radians = np.add(np.matmul(self._omega, input_data), self._beta)

        for index in range(self.qubit_count):
            quantum_program.inst(RX(rotation_radians[index], available_qubits[index]))

        return quantum_program

    @property
    def data_size(self) -> int:
        """The length of data vectors that can be encoded using this encoder."""
        return self._data_size


class EncoderPyquilThreshold(EncoderPyquil):
    """
    Encodes vectors of data into a quantum circuit as qubits in either the :math:`|0\\rangle` or :math:`|1\\rangle`
    state depending on whether they are less than or more than a given thresholding value, respectively.

    .. note::
        This encoder uses a number of qubits equal to the size of the input data, as such, it may not be suitable for
        large data without performing some chunking, an example of which can be seen in demonstration notebook
        `qxqfd_3_advanced.ipynb`.

    :Example:

        Create an encoder that takes data vectors of length 5 and thresholds at 3:

        >>> encoder = EncoderPyquilThreshold(qubit_count=5, threshold_value=3)
        >>> quantum_transformed_data = circuit_pyquil.run_program(input_data=test_data,
        ...                                                       encoder=encoder,
        ...                                                       decoder=DecoderPyquilRaw())

    :param qubit_count: The number of qubits in the circuits.
    :param threshold_value: Value at which the input value should be thresholded at. Data below this threshold will be
        encoded as :math:`|0\\rangle`, and those equal to or above will be encoded as :math:`|1\\rangle`.
    """

    def __init__(self, qubit_count: int, threshold_value: Any) -> None:
        super(EncoderPyquilThreshold, self).__init__(qubit_count=qubit_count)
        self._threshold_value = threshold_value

    def encode_qubits(self, input_data: Sequence[Any], available_qubits: List[int]) -> Program:
        """
        Encodes the given vector of data into a quantum circuit as qubits in either the :math:`|0\\rangle` or
        :math:`|1\\rangle` state depending on whether they are less than or more than a thresholding value,
        respectively.

        :param input_data: The data to be encoded.
        :param available_qubits: List of qubits that are available on the quantum backend. Supports use of custom
            lattices.
        :return: Contains the :py:class:`pyquil.gates.X` gates required to encode the qubits.
        """
        if len(input_data) != self.qubit_count:
            raise ValueError('input_data ({}) must be length {}.'.format(input_data, self.qubit_count))

        quantum_program = Program()

        for index in range(self.qubit_count):
            if input_data[index] >= self.threshold_value:
                quantum_program.inst(X(available_qubits[index]))
        return quantum_program

    @property
    def threshold_value(self) -> Any:
        """The thresholding value for input data."""
        return self._threshold_value

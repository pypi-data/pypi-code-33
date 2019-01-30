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

from typing import Any, Sequence

from qxbranch.quantum_feature_detector.circuit_base import CircuitBase
from qxbranch.quantum_feature_detector.encoder_base import EncoderBase
from qxbranch.quantum_feature_detector.decoder_base import DecoderBase, TDecodedResults
from qxbranch.quantum_feature_detector import logging_service


class QuantumFeatureDetector:
    """A class that applies quantum transforms to data to detect features.

    :Example:

        Build a :py:class:`QuantumFeatureDetector` from a :py:class:`CircuitPyquil` and apply it to some data.

        >>> circuit_generator_pyquil = CircuitGeneratorPyquil(qubit_count=5, gate_count=8)
        >>> qfd = QuantumFeatureDetector(circuit=circuit_generator_pyquil.generate())
        >>> qfd.apply_to_data(input_data=[0, 1, 4, 3, 9],
        ...                   encoder=EncoderPyquilThreshold(qubit_count=5, threshold_value=4),
        ...                   decoder=DecoderPyquilMeasurementSum())

    :param circuit: The circuit of transforms to use when detecting features.
    """

    def __init__(self, circuit: CircuitBase) -> None:
        self._logger = logging_service.get_logger(self.__class__.__name__)

        if isinstance(circuit, CircuitBase):
            self._circuit = circuit
        else:
            raise TypeError("circuit {} is not a valid Circuit".format(circuit))

    def apply_to_data(self, input_data: Sequence[Any], encoder: EncoderBase,
                      decoder: DecoderBase) -> TDecodedResults:
        """
        Transforms the given vector of data using the provided encoder, the built-in circuit, and the provided decoder.

        :param input_data: The input data to be transformed.
        :param encoder: Used to encode the given data onto the quantum feature detector circuit.
        :param decoder: Used to decode the results of the quantum feature detector back to classical data.
        :return: The quantum transformed data. The type of this object will depend on the decoder used.
        """
        if encoder.qubit_count != self.circuit.qubit_count:
            raise ValueError("Encoder {} has an incompatible qubit count with this QFD's circuit. It should encode {}"
                             "qubits.".format(encoder, self.circuit.qubit_count))
        return self._circuit.run_program(input_data=input_data, encoder=encoder, decoder=decoder)

    @property
    def circuit(self) -> CircuitBase:
        """The circuit used by this quantum feature detector."""
        return self._circuit

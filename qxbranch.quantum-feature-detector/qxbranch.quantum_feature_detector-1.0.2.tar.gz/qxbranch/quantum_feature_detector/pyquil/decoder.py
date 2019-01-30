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

from typing import Dict, List

from qxbranch.quantum_feature_detector.decoder_base import DecoderBase, TDecodedResults

MeasurementResultsPyquil = Dict[int, List[int]]


class Decoder(DecoderBase[MeasurementResultsPyquil, TDecodedResults]):
    """
    Decoder object that returns the raw measurement results. Use this decoder if you want to do all post-processing
    outside of the context of the :py:class:`QuantumFeatureDetector`.

    .. note:
        In the dictionary of raw values, the keys are the qubit indices, and the arrays are then the results for each
        individual trial. To get the result of trial `i`, for example, you would need to get the i-th entry from each
        qubit's array.

    :Example:
        Behavior for example pyquil results.

        >>> example_results = {0: array([0, 1, 1, 1, 0]), 1: array([0, 1, 0, 1, 1]),
        ...                    2: array([0, 1, 1, 1, 0])}
        >>> decoder = Decoder()
        >>> decoder.decode_measurement(measurement_results=example_results)
        {0: array([0, 1, 1, 1, 0]), 1: array([0, 1, 0, 1, 1]), 2: array([0, 1, 1, 1, 0])}
    """

    def __init__(self) -> None:
        super(Decoder, self).__init__()

    def decode_measurement(self, measurement_results: MeasurementResultsPyquil) -> MeasurementResultsPyquil:
        """
        Returns the raw circuit measurement values.

        :param measurement_results: The raw measured values from the :py:class:`Circuit`.
        :return: The raw measured values, though reduced to dimension 2 if necessary.
        """
        return measurement_results


class DecoderMostCommon(Decoder[List[int]]):
    """
    Decoder object that counts how often each unique result state occurred, then returns the most commonly occurring
    result as a list of 0 or 1 bits. If multiple results are equally common, the result that occurred first is used.

    :Example:
        Behavior for example pyquil results.

        >>> example_results = {0: array([0, 0, 0]), 1: array([1, 0, 1]),
        ...                    2: array([1, 0, 1]), 3: array([1, 1, 1]),
        ...                    4: array([0, 1, 0])}
        >>> decoder = DecoderMostCommon()
        >>> decoder.decode_measurement(measurement_results=example_results)
        [0, 1, 1, 1, 0]
    """

    def __init__(self) -> None:
        super(DecoderMostCommon, self).__init__()

    def decode_measurement(self, measurement_results: MeasurementResultsPyquil) -> List[int]:
        """
        Returns the most commonly occurring measurement value.

        :param measurement_results: The raw measured values from the :py:class:`Circuit`.
        :return: The most commonly occurring measurement value across all runs.
        """
        qubit_indices = list(measurement_results.keys())
        decoded_result = [[measurement_results[q][result] for q in qubit_indices]
                          for result in range(len(measurement_results[qubit_indices[0]]))]
        return max(decoded_result, key=decoded_result.count)


class DecoderMeasurementSum(Decoder[int]):
    """
    Decoder object that finds the most common result as per the :py:class:`DecoderMostCommon`, and
    returns the sum of the number of qubits measured to the :math:`|1\\rangle` state in that result.

    :Example:
        Behavior for example pyquil results. The most common result, with two occurrences, is `[0, 1, 1, 1, 0]`. The
        sum of the bits in this state is 3.

        >>> example_results = {0: array([0, 0, 0]), 1: array([1, 0, 1]),
        ...                    2: array([1, 0, 1]), 3: array([1, 1, 1]),
        ...                    4: array([0, 1, 0])}
        >>> decoder = DecoderMeasurementSum()
        >>> decoder.decode_measurement(measurement_results=example_results)
        3
    """

    def __init__(self) -> None:
        super(DecoderMeasurementSum, self).__init__()

    def decode_measurement(self, measurement_results: MeasurementResultsPyquil) -> int:
        """
        Returns a count of the qubits measured to state :math:`|1\\rangle` for the most commonly measured result.

        :param measurement_results: The raw measured values from the :py:class:`Circuit`.
        :return: A sum of the qubits measured in state :math:`|1\\rangle` for the most commonly occurring result.
        """
        qubit_indices = list(measurement_results.keys())
        decoded_result = [[measurement_results[q][result] for q in qubit_indices]
                          for result in range(len(measurement_results[qubit_indices[0]]))]
        most_common_result = max(decoded_result, key=decoded_result.count)
        return sum(most_common_result)

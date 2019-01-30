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
from typing import Generic, TypeVar

from qxbranch.quantum_feature_detector import logging_service

TMeasurementResults = TypeVar('TMeasurementResults')
TDecodedResults = TypeVar('TDecodedResults')


class DecoderBase(Generic[TMeasurementResults, TDecodedResults]):
    """
    Generic decoder object for inheriting. Decoders apply post-processing to the results of quantum circuits to
    interpret the measurements as classical information.
    """

    def __init__(self) -> None:
        self._logger = logging_service.get_logger(self.__class__.__name__)

    @abstractmethod
    def decode_measurement(self, measurement_results: TMeasurementResults) -> TDecodedResults:
        """Apply post-processing to decode measurement results from a quantum circuit to classical data."""
        raise NotImplementedError('Please implement this method')

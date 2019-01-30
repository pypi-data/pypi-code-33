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

"""
QxBranch's Quantum Feature Detector (QxQFD) is a Python library providing a class of quantum machine learning functions.
It provides a simple interface for using quantum transformations to detect features in data as part of a machine
learning application stack using Rigetti's Forest back-end.

For more information about QxBranch, please visit our website: https://qxbranch.com
"""

from .circuit import Circuit
from .circuit_generator import CircuitGenerator
from .decoder import Decoder, DecoderMostCommon, DecoderMeasurementSum
from .encoder import Encoder, EncoderQuantumKitchenSinks, EncoderThreshold


__all__ = ['Circuit',
           'CircuitGenerator',
           'Decoder', 'DecoderMostCommon', 'DecoderMeasurementSum',
           'Encoder', 'EncoderQuantumKitchenSinks', 'EncoderThreshold']

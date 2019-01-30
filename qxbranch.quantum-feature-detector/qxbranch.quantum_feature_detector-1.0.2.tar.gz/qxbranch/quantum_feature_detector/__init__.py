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
learning application stack.

For more information about QxBranch, please visit our website: https://qxbranch.com
"""

import logging
from typing import Union

_LOG_LEVEL = logging.INFO


def set_log_level(log_level: Union[str, int]):
    """Sets the log level to use for the package. Default log level is INFO.

    :Example:
        Set the log level to DEBUG at import time for all `qxbranch.quantum_feature_detector` modules.

        >>> import qxbranch.quantum_feature_detector as qxqfd
        >>> qxqfd.set_log_level('DEBUG')

    :param log_level: The level to set to, options:

        - CRITICAL or 5
        - ERROR or 4
        - WARNING or 3
        - INFO or 2
        - DEBUG or 1
    """
    global _LOG_LEVEL
    if log_level == 1 or log_level == 'DEBUG':
        _LOG_LEVEL = logging.DEBUG
    elif log_level == 2 or log_level == 'INFO':
        _LOG_LEVEL = logging.INFO
    elif log_level == 3 or log_level == 'WARNING':
        _LOG_LEVEL = logging.WARNING
    elif log_level == 4 or log_level == 'ERROR':
        _LOG_LEVEL = logging.ERROR
    elif log_level == 5 or log_level == 'CRITICAL':
        _LOG_LEVEL = logging.CRITICAL
    else:
        raise ValueError("log_level {} is not valid.".format(log_level))


# Import components of QxBranch's Quantum Feature Detectors

from .circuit_base import CircuitBase
from .circuit_generator_base import CircuitGeneratorBase
from .encoder_base import EncoderBase
from .decoder_base import DecoderBase
from .quantum_feature_detector import QuantumFeatureDetector
from .quantum_model import QuantumModel
from .quantum_transform import QuantumTransform
from . import pyquil

__all__ = ['CircuitBase',
           'CircuitGeneratorBase',
           'EncoderBase',
           'DecoderBase',
           'QuantumFeatureDetector',
           'QuantumModel',
           'QuantumTransform',
           'pyquil']

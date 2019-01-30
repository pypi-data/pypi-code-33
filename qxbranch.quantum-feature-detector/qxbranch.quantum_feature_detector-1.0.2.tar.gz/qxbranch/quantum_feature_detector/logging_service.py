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

import logging
import sys

from qxbranch.quantum_feature_detector import _LOG_LEVEL


class LoggingService:
    """Class to support class-by-class logging to StdOut."""
    initialized = False

    @classmethod
    def initialize_logging(cls):
        if not cls.initialized:
            level = _LOG_LEVEL
            handler = logging.StreamHandler(sys.stdout)
            handler.setLevel(level)
            formatter = logging.Formatter('%(asctime)s|%(name)-25s|%(levelname)-8s|%(message)s')
            handler.setFormatter(formatter)

            # It is necessary to set the level and handler on the root logger in case something like pytest
            # has already called basicConfig
            logging.root.setLevel(level)
            logging.root.addHandler(handler)
            cls.initialized = True


def get_logger(name: str):
    """Get a logger. `name` should be the name of the class the logger is instantiated for."""
    LoggingService.initialize_logging()
    return logging.getLogger(name)

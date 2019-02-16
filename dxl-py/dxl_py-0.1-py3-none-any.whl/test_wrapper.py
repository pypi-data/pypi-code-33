# coding=utf-8
# Copyright 2018 Hugo Ponte.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Tests for dxl_py wrapper.

To run these tests, make sure you have a configured/calibrated servo with ID set to 1.
"""

import time
import unittest
import logging
from dxl_py import wrapper

# Servo ids to test
SERVO_IDS = [1]


class WrapperTest(unittest.TestCase):

    def setUp(self):
        logging.basicConfig(level=logging.DEBUG)
        logging.debug('Running Tests.')
        logging.debug('These tests will use locally-connected servos %s' % SERVO_IDS)
        self.dxl_py = wrapper.DXLPy()

    def test_engage_disengage(self):
        self.dxl_py.engage()
        self.dxl_py.engage(engage=False)
        self.dxl_py.engage()

    def test_get_set_position(self):
        set_positions = [0.0, 0.5, 0.0, -0.5]
        for pos in set_positions:
            self.dxl_py.set({key: pos for key in SERVO_IDS})
            _ = self.dxl_py.get()
            time.sleep(1.0)

"""Tests for dxl_py.servos.

To run these tests, make sure you have a configured/calibrated servo with ID set to 1.
"""

import time
import unittest
import logging
from dxl_py import wrapper

# Servo names to test
SERVO_NAMES = ['test_servo']


class ServosTest(unittest.TestCase):

    def setUp(self):
        logging.basicConfig(level=logging.DEBUG, format="[%(filename)s:%(lineno)s - %(funcName)20s() ] %(message)s")
        logging.debug('Running Tests.')
        logging.debug('These tests will use locally-connected servos %s' % SERVO_NAMES)
        self.dxl_py = wrapper.DXLPy()

    def test_engage_disengage(self):
        self.dxl_py.engage()
        self.dxl_py.engage(engage=False)
        self.dxl_py.engage()

    def test_get_set_position(self):
        set_positions = [0.0, 0.5, 0.0, -0.5]
        for pos in set_positions:
            self.dxl_py.set({key: pos for key in SERVO_NAMES})
            _ = self.dxl_py.get()
            time.sleep(1.0)

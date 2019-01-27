#!/usr/bin/env python3
"""
TEST.STDLIB.TEST_SIGS.PY -- test script for SIGS module
Copyright (C) 2008-2015 by Peter A. Donis

Released under the GNU General Public License, Version 2
See the LICENSE and README files for more information

This script contains unit tests for the SIGS module in the
PLIB3.STDLIB sub-package.
"""

import os
import unittest
from signal import signal, SIGUSR1

from plib.stdlib.sigs import signal_handler


RESULT = [None]


def old_usr_handler(sig, frame):
    RESULT[0] = False


def usr_handler(sig, frame):
    RESULT[0] = True


class TestSigs(unittest.TestCase):
    
    def test_sigs(self):
        signal(SIGUSR1, old_usr_handler)  # because the default Python handler aborts the test
        with signal_handler(SIGUSR1, usr_handler):
            os.kill(os.getpid(), SIGUSR1)
            self.assertTrue(RESULT[0])
        os.kill(os.getpid(), SIGUSR1)
        self.assertFalse(RESULT[0])


if __name__ == '__main__':
    unittest.main()

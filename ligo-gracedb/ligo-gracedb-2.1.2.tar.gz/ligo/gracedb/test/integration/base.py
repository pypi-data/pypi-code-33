# -*- coding: utf-8 -*-
# Copyright (C) Brian Moe, Branson Stephens (2015)
#
# This file is part of gracedb
#
# gracedb is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# It is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with gracedb.  If not, see <http://www.gnu.org/licenses/>.
from __future__ import print_function
import unittest
import os

from ligo.gracedb.rest import GraceDb


class TestGraceDb(unittest.TestCase):
    """Base class for gracedb-client integration tests"""

    @classmethod
    def setUpClass(cls):

        # Define useful variables
        # Test service URL
        TEST_SERVICE = os.environ.get('TEST_SERVICE',
            'https://gracedb-test.ligo.org/api/')

        # A sleep time in seconds used to slow down the event creation requests
        cls.SLEEP_TIME = 1

        # Data directory
        cls.TEST_DATA_DIR = os.environ.get('TEST_DATA_DIR',
            os.path.join(os.path.dirname(__file__), "data"))

        # Set up client
        cls._gracedb = GraceDb(TEST_SERVICE)
        print("Using service {0}".format(cls._gracedb._versioned_service_url))

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
import unittest

from .test_events import TestEvents
from .test_labels import TestLabels
from .test_superevents import TestSuperevents
from .test_voevents import VOEventTestSuite

# List of TestCase classes to import tests from
test_classes = [TestEvents, TestSuperevents, TestLabels]

# List of test suites to add
test_suites = [VOEventTestSuite()]

# Define suite and loader
IntegrationTestSuite = unittest.TestSuite()
loader = unittest.TestLoader()

# Get suites from classes
for test_class in test_classes:
    suite = loader.loadTestsFromTestCase(test_class)
    test_suites.append(suite)

# Add custom test suites
for suite in test_suites:
    IntegrationTestSuite.addTest(suite)

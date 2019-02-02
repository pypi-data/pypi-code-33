#!/usr/bin/env python

"""
Run all tests of the project.
"""

import unittest

__author__ = "Tobias Rawald"
__copyright__ = "Copyright 2015, 2018 The PyRQA project"
__credits__ = ["Tobias Rawald",
               "Mike Sips"]
__license__ = "Apache-2.0"
__maintainer__ = "Tobias Rawald"
__email__ = "pyrqa@gmx.net"
__status__ = "Development"


if __name__ == "__main__":
    loader = unittest.TestLoader()

    print("\nRecurrence Plot Tests")
    print("=====================")

    recurrence_plot_suite = unittest.TestSuite()
    recurrence_plot_suite.addTests(
        loader.loadTestsFromName('pyrqa.variants.recurrence_plot.fixed_radius.test.Test'))

    unittest.TextTestRunner(verbosity=2).run(recurrence_plot_suite)

    print("\nRQA Tests")
    print("=========")

    rqa_suite = unittest.TestSuite()
    rqa_suite.addTests(
        loader.loadTestsFromName('pyrqa.variants.rqa.fixed_radius.test.Test'))

    unittest.TextTestRunner(verbosity=2).run(rqa_suite)

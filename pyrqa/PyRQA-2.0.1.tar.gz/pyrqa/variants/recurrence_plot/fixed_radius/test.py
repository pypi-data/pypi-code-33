#!/usr/bin/env python

"""
Testing recurrence plot implementations according to the fixed radius neighbourhood.
"""

import unittest

from pyrqa.selector import SingleSelector
from pyrqa.variants.base_test import BaseTest
from pyrqa.variants.recurrence_plot.fixed_radius.baseline import Baseline
from pyrqa.variants.recurrence_plot.fixed_radius.execution_engine import ExecutionEngine

from pyrqa.variants.recurrence_plot.fixed_radius.column_materialisation_uncompressed_byte import \
    ColumnMaterialisationUncompressedByte

VARIANTS = (ColumnMaterialisationUncompressedByte,)

__author__ = "Tobias Rawald"
__copyright__ = "Copyright 2015, 2018 The PyRQA project"
__credits__ = ["Tobias Rawald",
               "Mike Sips"]
__license__ = "Apache-2.0"
__maintainer__ = "Tobias Rawald"
__email__ = "pyrqa@gmx.net"
__status__ = "Development"


class Test(BaseTest):
    """
    Tests for RQA, Fixed Radius, OpenCL.
    """

    def perform_recurrence_analysis_computations(self,
                                                 settings,
                                                 opencl=None,
                                                 verbose=False,
                                                 edge_length=None,
                                                 selector=SingleSelector(),
                                                 variants_kwargs=None,
                                                 all_variants=False):
        if opencl:
            opencl.reset()

        if not edge_length:
            edge_length = Test.time_series.number_of_vectors

        baseline = Baseline(settings,
                            verbose=verbose)

        result_baseline = baseline.run()

        if all_variants:
            execution_engine = ExecutionEngine(settings,
                                               opencl=opencl,
                                               verbose=False,
                                               edge_length=edge_length,
                                               selector=selector,
                                               variants=VARIANTS,
                                               variants_kwargs=variants_kwargs)

            result = execution_engine.run()

            self.compare_recurrence_plot_results(result_baseline,
                                                 result)
        else:
            for variant in VARIANTS:
                execution_engine = ExecutionEngine(settings,
                                                   opencl=opencl,
                                                   verbose=False,
                                                   edge_length=edge_length,
                                                   selector=selector,
                                                   variants=(variant,),
                                                   variants_kwargs=variants_kwargs)

                result = execution_engine.run()

                self.compare_recurrence_plot_results(result_baseline,
                                                     result,
                                                     variant=variant)


if __name__ == "__main__":
    unittest.main()

import os
import unittest

import numpy as np

from chi1chi2.core.bulk_property import _get_alphas, _get_betas, _get_scale, _get_grouped_polars
from chi1chi2.core.property import Polar, Hyper
from chi1chi2.core.property_reader import PropsMol
from chi1chi2.utils.constants import Symmop


def file_for_test(file):
    return os.path.join(os.path.dirname(__file__), file)


SIMPLE_PROPS1 = file_for_test("simple_prop1.dat")
SIMPLE_PROPS2 = file_for_test("simple_prop2.dat")


class TestBulkProperty(unittest.TestCase):
    def test_get_alphas_for_lft(self):
        properties = [PropsMol.from_file(SIMPLE_PROPS1),
                      PropsMol.from_file(SIMPLE_PROPS2)]
        flags = [[True],
                 [True]]
        symmops = [Symmop.identity()]
        asym_groups = [[1, 2], [3, 2]]
        group1_partitioned = Polar(np.diag([50, 100, 150]))
        group2_partitioned = Polar(np.diag([150, 200, 250]))
        expected_alphas = [group1_partitioned, group1_partitioned,
                           group2_partitioned, group2_partitioned]

        alphas = _get_alphas("static", properties, flags, symmops, asym_groups)

        self.assertListEqual(expected_alphas, alphas)

    def test_get_alphas_for_lft_skp2(self):
        properties = [PropsMol.from_file(SIMPLE_PROPS1),
                      PropsMol.from_file(SIMPLE_PROPS2)]
        flags = [[True],
                 [False]]
        symmops = [Symmop.identity()]
        asym_groups = [[1, 2], [3, 2]]
        group1_partitioned = Polar(np.diag([50, 100, 150]))
        expected_alphas = [group1_partitioned, group1_partitioned]

        alphas = _get_alphas("static", properties, flags, symmops, asym_groups)

        self.assertListEqual(expected_alphas, alphas)

    def test_get_betas(self):
        properties = [PropsMol.from_file(SIMPLE_PROPS1),
                      PropsMol.from_file(SIMPLE_PROPS2)]
        flags = [[True],
                 [True]]
        symmops = [Symmop.identity()]
        asym_groups = [[1, 2], [5]]
        group1_partitioned = Hyper(np.arange(10, 280, 10).reshape((3, 3, 3)) / 2)
        group2_partitioned = Hyper(np.arange(40, 310, 10).reshape((3, 3, 3)))
        expected_betas = [group1_partitioned, group1_partitioned,
                          group2_partitioned]

        betas = _get_betas("static", properties, flags, symmops, asym_groups)

        self.assertListEqual(expected_betas, betas)

    def test_get_betas_skp(self):
        properties = [PropsMol.from_file(SIMPLE_PROPS1),
                      PropsMol.from_file(SIMPLE_PROPS2)]
        flags = [[True],
                 [False]]
        symmops = [Symmop.identity()]
        asym_groups = [[1, 2], [5]]
        group1_partitioned = Hyper(np.arange(10, 280, 10).reshape((3, 3, 3)) / 2)
        expected_betas = [group1_partitioned, group1_partitioned]

        betas = _get_betas("static", properties, flags, symmops, asym_groups)

        self.assertListEqual(expected_betas, betas)

    def test_scale(self):
        pol_stat = np.arange(1, 10).reshape((3, 3))
        pol_stat[0, 1] = 0
        pol_stat[1, 0] = 0
        pol_stat = Polar(pol_stat)
        pol_dyn = np.arange(2, 20, 2).reshape((3, 3))
        pol_dyn = Polar(pol_dyn)
        exptd_scale = np.ones((3, 3)) * 2
        exptd_scale[0, 1] = 0
        exptd_scale[1, 0] = 0

        scale = _get_scale(pol_stat, pol_dyn)

        self.assertListEqual(exptd_scale.tolist(), scale.tolist())

    def test_grouping_polars(self):
        dist_polars = Polar(np.arange(1, 10).reshape((3, 3))).to_distributed(5)
        dist_polars.polar_list.extend([Polar(np.arange(2, 20, 2).reshape((3, 3))) for i in range(5)])
        groups = [2, 1, 2, 4, 1]
        expt_polars = [n * dist_polars.polar_list[0].tensor for n in groups[:3]]
        expt_polars.extend([n * dist_polars.polar_list[5].tensor for n in groups[3:]])

        grouped_polars = _get_grouped_polars(groups, dist_polars, np.ones((3, 3)))

        for i in range(len(expt_polars)):
            self.assertListEqual(expt_polars[i].tolist(), grouped_polars[i].tolist())

    def test_get_alphas_qlft(self):
        properties = [PropsMol.from_file(SIMPLE_PROPS1),
                      PropsMol.from_file(SIMPLE_PROPS2)]
        flags = [[True],
                 [False]]
        symmops = [Symmop.identity()]
        asym_groups = [[1, 2], [3, 2]]
        group1_partitioned = Polar(np.diag([50, 100, 150]))
        expected_alphas = [group1_partitioned, group1_partitioned]

        alphas = _get_alphas("static", properties, flags, symmops, asym_groups)

        self.assertListEqual(expected_alphas, alphas)

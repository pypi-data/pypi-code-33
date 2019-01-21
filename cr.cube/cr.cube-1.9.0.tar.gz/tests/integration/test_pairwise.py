# encoding: utf-8
# pylint: disable=protected-access

"""Integration tests for pairwise comparisons."""

from unittest import TestCase
import pytest

import numpy as np

from cr.cube.crunch_cube import CrunchCube
from cr.cube.measures.pairwise_pvalues import PairwisePvalues

from ..fixtures import CR


# pylint: disable=missing-docstring, invalid-name, no-self-use
class TestStandardizedResiduals(TestCase):
    """Test cr.cube implementation of column family pairwise comparisons"""

    def test_same_col_counts(self):
        """Test statistics for columns that are all the same."""
        cube = CrunchCube(CR.SAME_COUNTS_3x4)
        pairwise_pvalues = PairwisePvalues(cube.slices[0], axis=0)
        expected = np.zeros([4, 4])
        actual = pairwise_pvalues._pairwise_chisq
        np.testing.assert_equal(actual, expected)

    def test_hirotsu_chisq(self):
        """Test statistic for hirotsu data matches R"""
        cube = CrunchCube(CR.PAIRWISE_HIROTSU_ILLNESS_X_OCCUPATION)
        pairwise_pvalues = PairwisePvalues(cube.slices[0], axis=0)
        expected = np.array(
            [
                [
                    0.0,
                    2.821910158116655,
                    0.9259711818781733,
                    12.780855448128131,
                    16.79727869630099,
                    0.924655442873681,
                    0.8008976269312448,
                    9.616972398702428,
                    1.4496863124510315,
                    18.556098937181705,
                ],
                [
                    2.821910158116655,
                    0.0,
                    1.6831132737959318,
                    8.683471852181562,
                    13.451053159265136,
                    0.38467827774871005,
                    1.5094961530071807,
                    9.081312924348003,
                    0.25833985406056126,
                    16.3533306337074,
                ],
                [
                    0.9259711818781733,
                    1.6831132737959318,
                    0.0,
                    24.348935423464653,
                    46.689386077899826,
                    0.18470822825752797,
                    1.376598707986204,
                    22.063658540387774,
                    1.0102118795109807,
                    47.62124004565971,
                ],
                [
                    12.780855448128131,
                    8.683471852181562,
                    24.348935423464653,
                    0.0,
                    0.8073979083263744,
                    8.490641259215641,
                    5.141740694105387,
                    1.2536004848874829,
                    3.576241745092247,
                    2.1974561987876613,
                ],
                [
                    16.79727869630099,
                    13.451053159265136,
                    46.689386077899826,
                    0.8073979083263744,
                    0.0,
                    11.792012011326468,
                    6.847609367845222,
                    0.743555569450378,
                    5.218390456727495,
                    0.725476017865348,
                ],
                [
                    0.924655442873681,
                    0.38467827774871005,
                    0.18470822825752797,
                    8.490641259215641,
                    11.792012011326468,
                    0.0,
                    0.7072537831958036,
                    7.620018353425002,
                    0.3321969685319031,
                    14.087591553810693,
                ],
                [
                    0.8008976269312448,
                    1.5094961530071807,
                    1.376598707986204,
                    5.141740694105387,
                    6.847609367845222,
                    0.7072537831958036,
                    0.0,
                    3.6724354409467352,
                    0.39674326208673527,
                    8.546159019524978,
                ],
                [
                    9.616972398702428,
                    9.081312924348003,
                    22.063658540387774,
                    1.2536004848874829,
                    0.743555569450378,
                    7.620018353425002,
                    3.6724354409467352,
                    0.0,
                    3.4464292421171003,
                    1.5916695633869193,
                ],
                [
                    1.4496863124510315,
                    0.25833985406056126,
                    1.0102118795109807,
                    3.576241745092247,
                    5.218390456727495,
                    0.3321969685319031,
                    0.39674326208673527,
                    3.4464292421171003,
                    0.0,
                    6.85424450468994,
                ],
                [
                    18.556098937181705,
                    16.3533306337074,
                    47.62124004565971,
                    2.1974561987876613,
                    0.725476017865348,
                    14.087591553810693,
                    8.546159019524978,
                    1.5916695633869193,
                    6.85424450468994,
                    0.0,
                ],
            ]
        )
        actual = pairwise_pvalues._pairwise_chisq
        np.testing.assert_almost_equal(actual, expected)

    def test_same_col_pvals(self):
        """P-values for columns that are all the same."""
        cube = CrunchCube(CR.SAME_COUNTS_3x4)
        expected = [np.ones([4, 4])]
        actual = cube.pairwise_pvals(axis=0)
        np.testing.assert_equal(actual, expected)

        # Assert correct exception in case of not-implemented direction
        with pytest.raises(NotImplementedError):
            cube.pairwise_pvals(axis=1)

    def test_hirotsu_pvals(self):
        cube = CrunchCube(CR.PAIRWISE_HIROTSU_ILLNESS_X_OCCUPATION)
        actual = cube.pairwise_pvals(axis=0)
        expected = [
            np.array(
                [
                    1,
                    0.999603716443816,
                    0.99999993076784,
                    0.435830186989942,
                    0.171365670494448,
                    0.999999931581745,
                    0.999999979427862,
                    0.726740806122402,
                    0.999997338047414,
                    0.105707739899106,
                    0.999603716443816,
                    1,
                    0.999991395396033,
                    0.806407150042716,
                    0.380296648898666,
                    0.999999999961875,
                    0.999996333717649,
                    0.773583582093158,
                    0.999999999998836,
                    0.192375246184738,
                    0.99999993076784,
                    0.999991395396033,
                    1,
                    0.017277623171216,
                    3.29012189337341e-06,
                    0.99999999999994,
                    0.999998237045896,
                    0.0365273119329589,
                    0.999999857555538,
                    2.23456306602809e-06,
                    0.435830186989942,
                    0.806407150042716,
                    0.017277623171216,
                    1,
                    0.999999977981595,
                    0.821586701043061,
                    0.982573114952466,
                    0.999999169027016,
                    0.998041030837588,
                    0.999934687968906,
                    0.171365670494448,
                    0.380296648898666,
                    3.29012189337341e-06,
                    0.999999977981595,
                    1,
                    0.52406354520284,
                    0.926322806048378,
                    0.99999998900118,
                    0.981100354607917,
                    0.999999991067971,
                    0.999999931581745,
                    0.999999999961875,
                    0.99999999999994,
                    0.821586701043061,
                    0.52406354520284,
                    1,
                    0.999999992799126,
                    0.883025655503086,
                    0.99999999998941,
                    0.33149560264078,
                    0.999999979427862,
                    0.999996333717649,
                    0.999998237045896,
                    0.982573114952466,
                    0.926322806048378,
                    0.999999992799126,
                    1,
                    0.997674862917282,
                    0.99999999995011,
                    0.81726901111794,
                    0.726740806122402,
                    0.773583582093158,
                    0.0365273119329589,
                    0.999999169027016,
                    0.99999998900118,
                    0.883025655503086,
                    0.997674862917282,
                    1,
                    0.998461227115608,
                    0.999994436499243,
                    0.999997338047414,
                    0.999999999998836,
                    0.999999857555538,
                    0.998041030837588,
                    0.981100354607917,
                    0.99999999998941,
                    0.99999999995011,
                    0.998461227115608,
                    1,
                    0.925999125959122,
                    0.105707739899106,
                    0.192375246184738,
                    2.23456306602809e-06,
                    0.999934687968906,
                    0.999999991067971,
                    0.33149560264078,
                    0.81726901111794,
                    0.999994436499243,
                    0.925999125959122,
                    1,
                ]
            ).reshape(10, 10)
        ]
        np.testing.assert_almost_equal(actual, expected)

    def test_odd_latent_dimensions(self):
        """Test code path for the pfaffian of an odd-dimensioned matrix
        Latent matrix size is (n_min - 1) so 3 for a 4x4 table.
        """
        cube = CrunchCube(CR.PAIRWISE_4X4)
        actual = cube.pairwise_pvals(axis=0)
        expected = [
            np.array(
                [
                    1,
                    0.949690252544668,
                    0.917559534718816,
                    0.97630069244232,
                    0.949690252544668,
                    1,
                    0.35511045473507,
                    0.999999119644564,
                    0.917559534718816,
                    0.35511045473507,
                    1,
                    0.313869429972919,
                    0.97630069244232,
                    0.999999119644564,
                    0.313869429972919,
                    1,
                ]
            ).reshape(4, 4)
        ]
        np.testing.assert_almost_equal(actual, expected)

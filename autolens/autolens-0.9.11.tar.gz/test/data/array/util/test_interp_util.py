import numpy as np
import pytest

from autolens.data.array import mask
from autolens.data.array.util import interp_util

class TestInterpGridFromGrid:

    def test__interp_grid_same_shape_as_grid__origin_is_y0_x0__no_buffer__interp_grid_is_grid(self):

        grid_1d = np.array([[1., -1.], [1., 0.], [1., 1.],
                            [0., -1.], [0., 0.], [0., 1.],
                            [-1., -1.], [-1., 0.], [-1., 1.]])

        interp_grid = interp_util.interp_grid_from_grid_and_interp_shape_and_origin(grid_1d=grid_1d, interp_shape=(3,3),
                                                                               interp_origin=(0.0, 0.0), buffer=0.0)

        assert (interp_grid == grid_1d).all()

    def test__interp_grid_same_shape_as_grid__origin_is_y0_x0__buffer_is_1__interp_grid_is_x2_grid(self):

        grid_1d = np.array([[1., -1.], [1., 0.], [1., 1.],
                            [0., -1.], [0., 0.], [0., 1.],
                            [-1., -1.], [-1., 0.], [-1., 1.]])

        interp_grid = interp_util.interp_grid_from_grid_and_interp_shape_and_origin(grid_1d=grid_1d, interp_shape=(3,3),
                                                                               interp_origin=(0.0, 0.0), buffer=1.0)

        assert interp_grid == pytest.approx(np.array([[2., -2.], [2., 0.], [2., 2.],
                                                      [0., -2.], [0., 0.], [0., 2.],
                                                      [-2., -2.], [-2., 0.], [-2., 2.]]), 1.0e-4)

    def test__interp_grid_shape_is_4x4__origin_is_y0_x0__buffer_is_0__interp_grid_is_grid(self):

        grid_1d = np.array([[1., -1.], [1., 0.], [1., 1.],
                            [0., -1.], [0., 0.], [0., 1.],
                            [-1., -1.], [-1., 0.], [-1., 1.]])

        interp_grid = interp_util.interp_grid_from_grid_and_interp_shape_and_origin(grid_1d=grid_1d, interp_shape=(4,4),
                                                                               interp_origin=(0.0, 0.0), buffer=0.0)

        f = (1.0/3.0)

        assert interp_grid == pytest.approx(np.array([[1., -1.], [1., -f], [1., f], [1., 1.],
                                                      [ f, -1.], [ f, -f], [ f, f], [f, 1.],
                                                      [-f, -1.], [-f, -f], [-f, f], [-f, 1.],
                                                      [-1., -1.], [-1., -f], [-1., f], [-1., 1.]]), 1.0e-4)

    def test__interp_grid_shape_is_3x4__origin_is_y0_x0__buffer_is_0__interp_grid_uses_grid_bounds(self):

        grid_1d = np.array([[1., -1.], [1., 0.], [1., 1.],
                            [0., -1.], [0., 0.], [0., 1.],
                            [-1., -1.], [-1., 0.], [-1., 1.]])

        interp_grid = interp_util.interp_grid_from_grid_and_interp_shape_and_origin(grid_1d=grid_1d, interp_shape=(3, 4),
                                                                               interp_origin=(0.0, 0.0), buffer=0.0)

        f = (1.0/3.0)

        assert interp_grid == pytest.approx(np.array([[1., -1.], [1., -f], [1., f], [1., 1.],
                                                      [0., -1.], [0., -f], [0., f], [0., 1.],
                                                      [-1., -1.], [-1., -f], [-1., f], [-1., 1.]]), 1.0e-4)

    def test__interp_grid_shape_is_4x3__origin_is_y0_x0__buffer_is_0__interp_grid_uses_grid_bounds(self):

        grid_1d = np.array([[1., -1.], [1., 0.], [1., 1.],
                            [0., -1.], [0., 0.], [0., 1.],
                            [-1., -1.], [-1., 0.], [-1., 1.]])

        interp_grid = interp_util.interp_grid_from_grid_and_interp_shape_and_origin(grid_1d=grid_1d, interp_shape=(4,3),
                                                                               interp_origin=(0.0, 0.0), buffer=0.0)

        f = (1.0/3.0)

        assert interp_grid == pytest.approx(np.array([[1., -1.], [1., 0], [1., 1.],
                                                      [ f, -1.], [ f, 0], [f, 1.],
                                                      [-f, -1.], [-f, 0], [-f, 1.],
                                                      [-1., -1.], [-1., 0], [-1., 1.]]), 1.0e-4)

    def test__move_origin_of_grid__coordinates_shift_to_around_origin(self):

        grid_1d = np.array([[1., -1.], [1., 0.], [1., 1.],
                            [0., -1.], [0., 0.], [0., 1.],
                            [-1., -1.], [-1., 0.], [-1., 1.]])

        interp_grid = interp_util.interp_grid_from_grid_and_interp_shape_and_origin(grid_1d=grid_1d, interp_shape=(3,3),
                                                                               interp_origin=(1.0, 0.0), buffer=0.0)

        assert (interp_grid == np.array([[0., -1.], [0., 0.], [0., 1.],
                                         [-1., -1.], [-1., 0.], [-1., 1.],
                                         [-2., -1.], [-2., 0.], [-2., 1.]])).all()


        interp_grid = interp_util.interp_grid_from_grid_and_interp_shape_and_origin(grid_1d=grid_1d, interp_shape=(3,3),
                                                                               interp_origin=(0.0, 1.0), buffer=0.0)

        assert (interp_grid == np.array([[1., -2.], [1., -1.], [1., 0.],
                                         [0., -2.], [0., -1.], [0., 0.],
                                         [-1., -2.], [-1., -1.], [-1., 0.]])).all()

        interp_grid = interp_util.interp_grid_from_grid_and_interp_shape_and_origin(grid_1d=grid_1d, interp_shape=(3,3),
                                                                               interp_origin=(1.0, 1.0), buffer=0.0)

        assert (interp_grid == np.array([[0., -2.], [0., -1.], [0., 0.],
                                         [-1., -2.], [-1., -1.], [-1., 0.],
                                         [-2., -2.], [-2., -1.], [-2., 0.]])).all()


# class TestInterpPairsAndWeightsFromGrids:
#
#     def test__interp_grid_is_2x2__one_coordinate_at_centre_of_grid__correct_pairs_and_weights(self):
#
#         # -1.0    0.0    1.0
#         #   ---------------
#         #  |       |       |
#         #  |   0   |   1   |
#         #  |-------x-------|
#         #  |       |       |
#         #  |   2   |   3   |
#         #  |---------------|
#
#         interp_grid = np.array([[0.5, -0.5], [0.5, 0.5],
#                                 [-0.5, -0.5], [-0.5, 0.5]])
#
#         grid = np.array([[-0.0e-4, 0.0e-4]])
#
#         pair_indexes, weights = interp_util.interp_pair_indexes_and_weights_from_interp_grid_and_grid(
#             interp_grid=interp_grid, grid=grid)
#
#         assert (pair_indexes == np.array([0, 1, 2, 3]))
#         assert weights == pytest.approx(np.array([0.25, 0.25, 0.25, 0.25]), 1.0e-4)
import numpy as np

from autolens.data.array.util import grid_util

def interp_grid_from_grid_and_interp_shape_and_origin(grid_1d, interp_shape, interp_origin, buffer=1.0e-8):

    y_min = np.min(grid_1d[:, 0]) - buffer
    y_max = np.max(grid_1d[:, 0]) + buffer
    x_min = np.min(grid_1d[:, 1]) - buffer
    x_max = np.max(grid_1d[:, 1]) + buffer

    pixel_scales = (float((y_max - y_min) / (interp_shape[0]-1)), float((x_max - x_min) / (interp_shape[1]-1)))

    interp_origin = (-1.0*interp_origin[0], -1.0*interp_origin[1]) # Coordinate system means we have to flip the origin

    return grid_util.regular_grid_1d_from_shape_pixel_scales_and_origin(shape=interp_shape, pixel_scales=pixel_scales,
                                                                        origin=interp_origin)

def interp_pair_indexes_and_weights_from_interp_grid_and_grid(interp_grid, grid):

    pair_indexes = np.zeros(shape=(grid.shape[0], 4))
    weights = np.zeros(shape=(grid.shape[0], 4))


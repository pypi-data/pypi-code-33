import pyproj
import numpy as np
from shapely.geometry import shape
from shapely.ops import transform
from functools import partial

class polygon_utils(object):

    @staticmethod
    def utm_area_of_latlng_polygon(p):
        g = {'type': 'Polygon',
             'coordinates': p}
        s = shape(g)
        proj = partial(pyproj.transform, pyproj.Proj(init='epsg:4326'),
                       pyproj.Proj(init='epsg:3857'))
        projected_area = transform(proj, s).area
        return projected_area

    @staticmethod
    def centroid_of_bounds(b):
        return [0.5 * (b[3] + b[1]), 0.5 * (b[2] + b[1])]

    @staticmethod
    def centroid_of_polygon(p):
        g = {'type': 'Polygon',
             'coordinates': p}
        s = shape(g)
        return s.centroid

    @staticmethod
    def bounds(p):
        return [
            min([lng for lat,lng in p]),
            min([lat for lat,lng in p]),
            max([lng for lat,lng in p]),
            max([lat for lat,lng in p]),
        ]

    @staticmethod
    def coordinates_from_bounds(b):
        coordinates = [[b[1], b[0]], [b[1], b[2]], [b[3], b[2]], [b[3], b[0]], [b[1], b[0]]]
        return coordinates

    @staticmethod
    def tiles_to_bounds(samples, image_bounds, image_size):
        # Rasterio cubes are (0,0) in the upper left corner, and the first axis is the y/lat coordinate.
        # Bounds are left, lower, right, upper in lat lng.
        dlat_per_pixel = np.abs(image_bounds[2] - image_bounds[0]) / image_size[1]
        dlng_per_pixel = np.abs(image_bounds[3] - image_bounds[1]) / image_size[0]

        b = [[image_bounds[0] + s["x"] * dlng_per_pixel,
              image_bounds[3] - s["y"] * dlat_per_pixel,
              image_bounds[0] + (s["x"] + s["dx"]) * dlng_per_pixel,
              image_bounds[3] - (s["y"] + s["dy"]) * dlat_per_pixel] for s in samples]
        return b

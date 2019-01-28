import math
radius_of_earth_m = 6378137.0
layer_resolution_m = 30.0
delta_arc_per_pixel = 1.0 * layer_resolution_m * layer_resolution_m / radius_of_earth_m

class tiler_utils(object):

    @staticmethod
    def _polygon_from_bounds(b):
        coordinates = [[b[1], b[0]], [b[1], b[2]], [b[3], b[2]], [b[3], b[0]], [b[1], b[0]]]
        return coordinates

    @staticmethod
    def tile_up_bounds(bounds, tile_size):

        stack_of_coordinates = []

        delta_arc = tile_size * delta_arc_per_pixel
        lng = bounds[0]
        while lng < bounds[2]:
            lat = bounds[1]
            while lat < bounds[3]:
                stack_of_coordinates.append(tiler_utils._polygon_from_bounds([lng, lat, lng+delta_arc, lat+delta_arc]))
                lat += delta_arc
            lng += delta_arc

    @staticmethod
    def latlng_to_tile_xyz(latlng, zoom):
        lat_rad = math.radians(latlng[0])
        n = 1.0 * (2 ** zoom)
        x = int((latlng[1] + 180.0) / 360.0 * n)
        y = int((1.0 - math.log(math.tan(lat_rad) + (1 / math.cos(lat_rad))) / math.pi) / 2.0 * n)
        return [x, y]

    @staticmethod
    def tile_xyz_to_latlng_of_nw_corner(xy, zoom):
        n = 1.0 * (2 ** zoom)
        lon_deg = xy[0] / n * 360.0 - 180.0
        lat_rad = math.atan(math.sinh(math.pi * (1.0 - 2.0 * xy[1] / n)))
        lat_deg = math.degrees(lat_rad)
        return [lat_deg, lon_deg]

    @staticmethod
    def tile_xyz_to_latlng_polygon_coordinates(xy, zoom):
        nw = tiler_utils.tile_xyz_to_latlng_of_nw_corner(xy, zoom)
        se = tiler_utils.tile_xyz_to_latlng_of_nw_corner([xy[0]+1, xy[1]+1], zoom)
        return tiler_utils._polygon_from_bounds([nw[1], se[0], se[1], nw[0]])

    @staticmethod
    def bounds_to_xyz_tileset(bounds, zoom):
        nw_xy = tiler_utils.latlng_to_tile_xyz([bounds[3], bounds[0]], zoom)
        se_xy = tiler_utils.latlng_to_tile_xyz([bounds[1], bounds[2]], zoom)
        tiles = [[x, y] for x in range(nw_xy[0], se_xy[0]+1) for y in range(nw_xy[1], se_xy[1]+1)]
        return tiles




import pyproj
from pyproj import Proj, transform
from aether.dataobjects.AEPolygon import AEPolygon
import json


class geometry_utils(object):

    _latlng_projection = "epsg:4326"

    @staticmethod
    def transform_utm_to_pixels(src, utm_polygon):
        colrow_pixels = []
        bounds_window = src.window(*utm_polygon.to_bounds())
        for p in utm_polygon.lnglats():
            # Window returns (col_off, row_off, width, height)
            # BoundingBox (the input) expects (left, bottom, right, top), which is equivalent to (lng, lat) order.
            # ColRow on an image is equivalent to LngLat
            w = src.window(*(p+p))
            colrow_pixels.append([w.col_off - bounds_window.col_off, w.row_off - bounds_window.row_off])
        return AEPolygon().from_lnglats(colrow_pixels)

    @staticmethod
    def transform_to_latlng(data_crs, polygons):
        p_latlng = pyproj.Proj(init=geometry_utils._latlng_projection)
        from_proj = pyproj.Proj(data_crs)
        pixel_polygons = geometry_utils._transform_geometries(polygons, from_proj, p_latlng)
        return pixel_polygons

    @staticmethod
    def latlng_to_src_pixels(src, polygon):
        utm_polygon = geometry_utils.transform_latlng_to_pixels(src.meta["crs"], [polygon])[0]
        polygon_window = src.window(*utm_polygon.to_bounds())
        return polygon_window

    @staticmethod
    def transform_latlng_to_pixels(data_crs, polygons):
        p_latlng = pyproj.Proj(init=geometry_utils._latlng_projection)
        p_pixel = pyproj.Proj(data_crs)
        pixel_polygons = geometry_utils._transform_geometries(polygons, p_latlng, p_pixel)
        return pixel_polygons

    # Assumes bounds is array or BoundingBox representation (left, bottom, right, top)
    # Polygons are counterclockwise when external boundaries.
    @staticmethod
    def transform_geotiff_meta_bounds_into_latlng(data_crs, bounds):
        inProj = Proj(data_crs)
        outProj = Proj(init=geometry_utils._latlng_projection)

        lnglat = []
        lnglat.append(transform(inProj, outProj, bounds[0], bounds[1]))
        lnglat.append(transform(inProj, outProj, bounds[2], bounds[1]))
        lnglat.append(transform(inProj, outProj, bounds[2], bounds[3]))
        lnglat.append(transform(inProj, outProj, bounds[0], bounds[3]))
        lnglat.append(transform(inProj, outProj, bounds[0], bounds[1]))
        return AEPolygon().from_lnglats(lnglat)

    @staticmethod
    # Notice that pyproj uses the lng-lat convention not the lat-lng convention.
    def _transform_geometries(polygons, from_proj, to_proj):
        new_polygons = []
        for polygon in polygons:
            plngs, plats = pyproj.transform(from_proj, to_proj, polygon.lngs(), polygon.lats())
            new_polygons.append(AEPolygon().from_lats_and_lngs(plats, plngs))
        return new_polygons

    @staticmethod
    def polygons_as_geojson(polygons_as_coordinates, crs_name, polygon_properties_dict=None):
        if polygon_properties_dict is None:
            polygon_properties_dict = [{}] * len(polygons_as_coordinates)

        features = []
        for polygon_id, polygon in enumerate(polygons_as_coordinates):
            features.append(dict(
                type="Feature",
                geometry=dict(
                    type="Polygon",
                    coordinates=[polygon], # Remember, coordinates is a list of polygons.
                ),
                properties=polygon_properties_dict[polygon_id]
            ))

        g = dict(type="FeatureCollection",
                 crs=dict(
                     type="name",
                     properties=dict(
                         name=str(crs_name),
                     )
                 ),
                 features=features
                 )
        return json.dumps(g)

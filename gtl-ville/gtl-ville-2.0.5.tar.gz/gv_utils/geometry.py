#!/usr/bin/env python3
# -*- coding: UTF-8 -*-

import math

import shapely.geometry
import shapely.geos
import shapely.wkb

from gv_utils import enums


LAT = enums.AttId.lat
LON = enums.AttId.lon
X = enums.AttId.x
Y = enums.AttId.y

CENTER = {LAT: 45.17475, LON: 5.74626}
SRID = 4326


def latlon_to_xy(latlon, center=None):
    if center is None:
        center = CENTER

    lat = latlon.get(LAT, 0) * math.pi / 180
    lon = latlon.get(LON, 0) * math.pi / 180
    latcenter = center.get(LAT, 0) * math.pi / 180
    loncenter = center.get(LON, 0) * math.pi / 180

    r = 6371000  # earth radius in meters
    x = r * math.cos(lat) * math.sin(lon - loncenter)
    y = r * (math.cos(latcenter) * math.sin(lat) - math.sin(latcenter) * math.cos(lat) * math.cos(lon - loncenter))
    return {X: x, Y: y}


def round_latlon(latlon):
    return {LAT: round(latlon.get(LAT, 0) * 10000), LON: round(latlon.get(LON, 0) * 10000)}


def close_elems_it(latlonrounded, latlonmatrix, radius=1):
    lat, lon = latlonrounded.get(LAT, 0), latlonrounded.get(LON, 0)
    for i in [lat, lat+radius, lat-radius]:
        if i in latlonmatrix:
            for j in [lon, lon+radius, lon-radius]:
                if j in latlonmatrix[i]:
                    for elem in latlonmatrix[i][j]:
                        yield elem


def xy_distance(fromxy, toxy):
    return math.sqrt((fromxy.get(X, 0) - toxy.get(X, 0))**2 +
                     (fromxy.get(Y, 0) - toxy.get(Y, 0))**2)


def xy_bearing(fromxy, toxy):
    radbearing = math.atan2(toxy.get(X, 0) - fromxy.get(X, 0), toxy.get(Y, 0) - fromxy.get(Y, 0))
    degbearing = math.degrees(radbearing)
    return int((degbearing + 360) % 360)


def encode_geometry(geometry):
    if not hasattr(geometry, '__geo_interface__'):
        raise TypeError('{g} does not conform to '
                        'the geo interface'.format(g=geometry))
    shape = shapely.geometry.asShape(geometry)
    shapely.geos.lgeos.GEOSSetSRID(shape._geom, SRID)
    return shapely.wkb.dumps(shape, include_srid=True)


def decode_geometry(wkb):
    return shapely.wkb.loads(wkb)

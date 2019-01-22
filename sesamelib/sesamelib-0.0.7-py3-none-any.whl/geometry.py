# -*- coding: utf-8 -*-
import logging
import numpy as np
from osgeo import ogr
import sys
import xml.etree.ElementTree as ET


# NOTE(msimonin): Python is a bit conservative with the recursion level (And I
# don't want to rewrite in a imperative way...)
sys.setrecursionlimit(100000)


LIMIT_INTERIOR = 1000


logger = logging.getLogger(__name__)


def points_geometry(geometry):
    """
    Returns the groups of list of points that composed a geometry.

    A geometry in our context is a multisurface. A surface is a connex part of
    the eez composed of an exterior polygon and many interior polygons.
    E.G: http://www.marineregions.org/gazetteer.php?p=details&id=5676 is
    composed of one exterior polygons an more than 17K interior polygons
    representing the islands

    Args:
        geometry (ogr.Geometry): the geometry

    Returns:
        List of List of points.
    """
    if geometry.GetPoints() is not None:
        return [geometry.GetPoints()]
    else:
        count = geometry.GetGeometryCount()
        points = []
        for idx in range(count):
            pts = points_geometry(geometry.GetGeometryRef(idx))
            points.extend(pts)
    return points


def _update_not_none(geometry, key, value):
    if value is None:
        geometry.update({key: "No value for %s" % key})
    else:
        geometry.update({key: value.text})


def load_geometry(gml_path, only_exteriors=False, dTolerance=None):
    """
    Loads the Geometry from a gml file.

    Args:
        gml_path (str): path to the GML file
        only_exteriors (bool): True iff we must only consider the external
            polygons
        dTolerance (float): If given, The polygon will be simplified using the

    Returns
        a dict:
        {
            "name": name of the eez (str)
            "eez" : file path to the gml file (str)
            "geometry": ogr.Geometry
            "points": points that compose the geometry (list of list)
        }
    """

    tree = ET.parse(gml_path)
    root = tree.getroot()

    name =  root.find(".//{geo.vliz.be/MarineRegions}geoname")
    mrgid =  root.find(".//{geo.vliz.be/MarineRegions}mrgid")

    geometry = {"eez": gml_path}

    _update_not_none(geometry, "name", name)
    _update_not_none(geometry, "mrgid", mrgid)


    multisurface = root.findall(".//{http://www.opengis.net/gml}MultiSurface")

    if len(multisurface) != 1:
        logger.error("[%s] We found %s multisurface" % (gml_path, len(multisurface)))
        return None

    geometry.update({"type": "full"})
    if only_exteriors:
        # we remove all the interiors polygons first
        polygons = root.findall(".//{http://www.opengis.net/gml}Polygon")
        for p in polygons:
            interiors = p.findall(".//{http://www.opengis.net/gml}interior")
            for interior in interiors:
                p.remove(interior)
        geometry.update({"type": "only_exteriors"})

    geom = ogr.CreateGeometryFromGML(ET.tostring(multisurface[0], encoding="unicode"))

    if dTolerance is not None:
        geom = geom.SimplifyPreserveTopology(dTolerance)
        geometry.update({"type": "simplified-%s" % dTolerance})


    geometry.update({
        "geometry": geom
    })

    # NOTE(msimonin): we treat the first levels differently as it contains all
    # the exteriors.
    for idx in range(geom.GetGeometryCount()):
        geometry.setdefault("points", [])
        geometry["points"].append(points_geometry(geom.GetGeometryRef(idx)))

    return geometry


def plot_zone(ax, geometry):
    """
    Draw lines corresponding to the zone.

    The exterior lines are plotted first, the number of interior lines are
    limited to LIMIT_INTERIOR

    Args:
        ax (matplotlib.axes): the axes where to plot the points
        geometry (dict): The geometry to plot
    """
    for lines in geometry["points"]:
        for line in lines[0:LIMIT_INTERIOR]:
            # plotting
            x = [x for x,_ in line]
            y = [y for _,y in line]
            # NOTE(msimonin): inverting x et y for plotting
            ax.plot(y, x)
            ax.set_title("%s - %s" % (geometry["name"], geometry["mrgid"]))
    return ax


def distance(x, y, geometry):
    """Compute the distance between a geo point and the geometry

    Args:
       x (double): x
       y (double): y
       geometry (dict): The geometry

    Returns
      The distance
    """
    logging.debug("Computing the distance with %s - %s", x, y)
    g = geometry["geometry"]
    point = ogr.Geometry(ogr.wkbPoint)
    point.AddPoint(x, y)
    d = point.Distance(g)
    return d


def within(x, y, geometry):
    """Tell if a point is in a geometry

    Args:
       x (double): x
       y (double): y
       geometry (dict): The geometry

    Returns
      True iff the pont is inside the geometry
    """
    #logging.debug("Computing the distance with %s - %s", x, y)
    g = geometry["geometry"]
    point = ogr.Geometry(ogr.wkbPoint)
    point.AddPoint(x, y)
    d = point.Within(g)
    return d


def index_geometries(geometries, cell_size=1):
    """
    Index the geometry by points on a grid

    Args:
      geometries (list): the list of geometries to index (as given by
        load_geometry)

    Returns:
      An index (dict) structure as follow:
    {
        "eezs":
        {
            # for each zone id maps the geometry dict as
            # returned by the load_geometry function
            "mrgid-1": {geometry}
            "mrgid-2": {geometry}
            ...
        },
        "index":
        {
            # for each point on the grid maps the closest zones
            (-90.0, -180.0): ["mrgid-x", "mrgid-y"],
            (-90.0, -179.0): ["mrgid-z"]
        }
        "cell_size": 1
    }
    """
    # Make data.
    X = np.arange(-90.0, 90.0, cell_size)
    Y = np.arange(-180.0, 180.0, cell_size)
    index = {}
    for x in X:
        for y in Y:
            logging.debug("(x, y) = (%s, %s)" % (x, y))
            m = sys.maxsize
            mins = []
            for g in geometries:
                d = distance(x, y, g)
                if d < m:
                    mins = []
                    m = d
                if d <= m:
                    mins.append(g["mrgid"])

            index[(x,y)] = mins
            logging.info("(%s,%s) -> %s" % (x, y, index[(x,y)]))

    return {
        "eezs": dict([[g["mrgid"], g] for g in geometries]),
        "index": index,
        "cell_size": cell_size
    }

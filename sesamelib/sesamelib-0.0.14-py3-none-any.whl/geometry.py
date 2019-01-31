# -*- coding: utf-8 -*-
import logging
import numpy as np
from osgeo import ogr
import sys
import xml.etree.ElementTree as ET


# NOTE(msimonin): Python is a bit conservative with the recursion level (And I
# don't want to rewrite in a imperative way...)
sys.setrecursionlimit(100000)


# Limit the number of internal polygons to consider
# 1000 is probably too much ! (for drawing purpose)
LIMIT_INTERIOR = 1000


# whether single envelope should be considered
# a single envelope is the envelope that encompass all the surfaces
ENVELOPE_SINGLE = 0
# This indicates that the geometry will be composed of one rectangle per surface
ENVELOPE_MULTI = 1
# No enveloppe let the geometry as it is
ENVELOPE_NONE = -1


logger = logging.getLogger(__name__)


def _create_geom_from_envelope(geom):
    """Creates a geometry from the enveloppe of another.

    Args:
        geom: the geometry to get the envelope from
    """
    x1, x2, y1, y2 = geom.GetEnvelope()
    ring = ogr.Geometry(ogr.wkbLinearRing)
    ring.AddPoint_2D(x1, y1)
    ring.AddPoint_2D(x2, y1)
    ring.AddPoint_2D(x2, y2)
    ring.AddPoint_2D(x1, y2)
    ring.AddPoint_2D(x1, y1)
    poly = ogr.Geometry(ogr.wkbPolygon)
    poly.AddGeometry(ring)
    return poly

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


class SesameGeometry:

    def __init__(self):
        """Constructor, use the classmethod below instead"""

        # Human readable name
        self.name = None
        # the marine region id of the zone
        self.mrgid = None
        # True iff only the external polygons are considered
        self.only_exteriors = None
        # dTolerance factor
        self.dTolerance = None
        # True iff only the envelope is considered
        self.envelope = None
        # Total points that compose the geometry
        self.total_points = None
        # The underlying geometry
        self.total_polygons = None
        self._geometry = None
        # The list of points
        # This is maps the hierarchy of the geometry
        # [ [[][][]] [] ]  first level is the connex parts (surfaces)
        #                  second level is the polygons
        #                  (one external + several external)
        self._points = None

    @classmethod
    def from_gml_file(cls,
                      gml_path,
                      only_exteriors=False,
                      dTolerance=0.0,
                      envelope=ENVELOPE_NONE):
        self = cls()
        tree = ET.parse(gml_path)
        root = tree.getroot()

        self.name =  root.find(".//{geo.vliz.be/MarineRegions}geoname")
        self.name = self.name.text if self.name is not None else ""
        self.mrgid =  root.find(".//{geo.vliz.be/MarineRegions}mrgid")
        self.mrgid = self.mrgid.text if self.mrgid is not None else ""
        self.only_exteriors = only_exteriors
        self.dTolerance = dTolerance
        self.envelope = envelope
        if self.envelope == ENVELOPE_MULTI:
            # we consider only the external polygons for the multi envelope case
            self.only_exteriors = True

        multisurface = root.findall(".//{http://www.opengis.net/gml}MultiSurface")
        if len(multisurface) != 1:
            logger.error("[%s] We found %s multisurface" % (gml_path, len(multisurface)))
            # raise something
            return None

        if self.only_exteriors:
            # we remove all the interiors polygons first
            polygons = root.findall(".//{http://www.opengis.net/gml}Polygon")
            for p in polygons:
                interiors = p.findall(".//{http://www.opengis.net/gml}interior")
                for interior in interiors:
                    p.remove(interior)

        # create a geometry from what we have
        geom = ogr.CreateGeometryFromGML(ET.tostring(multisurface[0], encoding="unicode"))
        # simplify it
        geom = geom.SimplifyPreserveTopology(dTolerance)

        # consider the envelope case
        if envelope == ENVELOPE_SINGLE:
            geom = _create_geom_from_envelope(geom)
        elif envelope == ENVELOPE_MULTI:
            multipolygon = ogr.Geometry(ogr.wkbMultiPolygon)
            for idx in range(geom.GetGeometryCount()):
                _geom = _create_geom_from_envelope(geom.GetGeometryRef(idx))
                multipolygon.AddGeometry(_geom)
            geom = multipolygon


        # NOTE(msimonin): we treat the first levels differently as it contains all
        # the exteriors.
        points = []
        for idx in range(geom.GetGeometryCount()):
            points.append(points_geometry(geom.GetGeometryRef(idx)))

        # Finally compute some data about the points / polygons
        total_polygons = 0
        total_points = 0
        for lines in points:
            total_polygons += len(lines)
            for line in lines:
                total_points += len(line)

        self.points = points
        self.total_polygons = total_polygons
        self.total_points = total_points
        self._geometry = geom

        return self

    def to_dict(self):
        return {
            "name": self.name,
            "mrgid": self.mrgid,
            "only_exteriors": self.only_exteriors,
            "dTolerance": self.dTolerance,
            "envelope": self.envelope,
        }

    def distance(self, x, y, enlarge=0.0):
        point = ogr.Geometry(ogr.wkbPoint)
        point.AddPoint(x, y)
        d = point.Distance(self._geometry) - enlarge
        return d


def plot_zone(ax, geometry):
    """
    Draw lines corresponding to the zone.

    The exterior lines are plotted first, the number of interior lines are
    limited to LIMIT_INTERIOR

    Args:
        ax (matplotlib.axes): the axes where to plot the points
        geometry (dict): The geometry to plot
    """
    logger.info("plot_zone for geometry.mrgid={}".format(geometry.mrgid))
    for lines in geometry.points:
        for line in lines[0:LIMIT_INTERIOR]:
            # plotting
            x = [x for x,_ in line]
            y = [y for _,y in line]
            # NOTE(msimonin): inverting x et y for plotting
            ax.plot(y, x)
            ax.set_title("%s - %s" % (geometry.name, geometry.mrgid))
    return ax


def distance(x, y, geometry, enlarge=0.0):
    """Compute the distance between a geo point and the geometry

    Args:
       x (double): x
       y (double): y
       geometry (dict): The geometry
       enlarge (double): act as if the geometry was bigger by adding
                         substracting this to the real distance

    Returns
      The distance
    """
    logging.debug("Computing the distance with %s - %s", x, y)
    return geometry.distance(x, y, enlarge=enlarge)


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
                    mins.append(g.mrgid)

            index[(x,y)] = mins
            logger.info("(%s,%s) -> %s" % (x, y, index[(x,y)]))

    return {
        "eezs": dict([[g.mrgid, g] for g in geometries]),
        "index": index,
        "cell_size": cell_size
    }

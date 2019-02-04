# -*- coding: utf-8 -*-
import copy
from collections import defaultdict
import logging
import math
import numpy as np
from osgeo import ogr
import sys
import xml.etree.ElementTree as ET


# NOTE(msimonin): Python is a bit conservative with the recursion level (And I
# don't want to rewrite in a imperative way...)
sys.setrecursionlimit(100000)


# Limit the number of internal polygons to consider
# 1000 is probably too much ! (for drawing purpose)
LIMIT_INTERIOR = 100


# whether single envelope should be considered
# a single envelope is the envelope that encompass all the surfaces
ENVELOPE_SINGLE = 0
# This indicates that the geometry will be composed of one rectangle per surface
ENVELOPE_MULTI = 1
# Make the union of the multiple envelope
ENVELOPE_MULTI_UNION = 2
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
        if self.envelope in [ENVELOPE_MULTI, ENVELOPE_MULTI_UNION]:
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
        if self.envelope == ENVELOPE_SINGLE:
            geom = _create_geom_from_envelope(geom)
        elif self.envelope in [ENVELOPE_MULTI, ENVELOPE_MULTI_UNION]:
            _geoms = []
            for idx in range(geom.GetGeometryCount()):
                _geom = _create_geom_from_envelope(geom.GetGeometryRef(idx))
                _geoms.append(_geom)

            multipolygon = ogr.Geometry(ogr.wkbMultiPolygon)
            multipolygon.AddGeometry(_geoms[0])
            for _geom in _geoms[1:]:
                if self.envelope == ENVELOPE_MULTI:
                    print("building envelope multi")
                    multipolygon.AddGeometry(_geom)
                else:
                    multipolygon = multipolygon.Union(_geom)

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
        point.AddPoint_2D(x, y)
        d = point.Distance(self._geometry) - enlarge
        return d

    def intersect(self, x1, y1, x2, y2):
        """
        Tells if the segment [(x1, y1), (x2, y2)] intersect the geometry

        Args:
            x1 (double): x value of the first point
            y1 (double): y value of the first point
            x2 (double): x value of the second point
            y2 (double): y value of the second point

        Returns:
            True iff the segment intesect the geometry
        """
        line = ogr.Geometry(ogr.wkbLineString)
        line.AddPoint_2D(x1, y1)
        line.AddPoint_2D(x2, y2)

        return line.Intersect(self._geometry)

    def ogr_contains(self, other):
        return self._geometry.Contains(other)

    def ogr_intersects(self, other):
        return self._geometry.Intersects(other)

class MrgidInfo:
    """Precompute stuffs about a mrgid regarding a cell."""
    def __init__(self):
        self.within = False
        self.intersect = False
        self.corner_distances = []


class IndexedCell:
    """A cell is the unit when indexing the zones.

    A cell represent a portion of the globe (most probably) a rectangle patch.
    The purpose is to answer quickly the question :

    given (x,y) \in cell, what is the distance to one arbitrary given zone ?
    """

    def __init__(self):
        # record the cell points
        self._corners = []
        # set of mrgids
        self._distances_by_mrgids = defaultdict(list)
        # we shouldn't save this here
        self._geometries_by_mrgids = {}

        self.mrgids_info = {}

    def add_corner(self, x, y, geoms_with_distances):
        for g, d in geoms_with_distances:
            self._geometries_by_mrgids[g.mrgid] = g
            self._distances_by_mrgids[g.mrgid].append(d)
        self._corners.append((x, y))
        return self

    def finalize(self):
        """Finish precomputing stuffs"""

        # compute within and intersect for each geometry
        # we could uniq the geometries before ()

        # build the polygon representing the cell
        ring = ogr.Geometry(ogr.wkbLinearRing)
        ring = ogr.Geometry(ogr.wkbLinearRing)
        for x, y in self._corners + [self._corners[0]]:
            ring.AddPoint(x, y)

        poly = ogr.Geometry(ogr.wkbPolygon)
        poly.AddGeometry(ring)

        for mrgid, geom in self._geometries_by_mrgids.items():
            # build the MrgidInfo
            logger.debug("|-Precalculating within/intersect for %s" % mrgid)
            self.mrgids_info.setdefault(mrgid, MrgidInfo())
            mrgid_info = self.mrgids_info[mrgid]
            mrgid_info.within = geom.ogr_contains(poly)
            mrgid_info.intersect = geom.ogr_intersects(poly)
            mrgid_info.corner_distances = self._distances_by_mrgids[mrgid]

        # NOTE(msimonin): don't save the geometries
        self._geometries_by_mrgids = None
        self._distances_by_mrgids = None
        return self

    def _distance(self, x, y, geom):
        """For each zone returns the closest zone and the associated distance.


        NOTE: x, y is required to be within the current cell. This should be
              enforced by the Index lookup.

        - if the cell is within (=> intersects): d = 0 (no heavy computation)
        - if the cell is not within but intersects: compute d (might be heavy)
        - if the cell is not within and not intersects: take the max of the 4
          This probably overestimates the real distance by at most cell_size
        distances of the cell points
        """
        logger.debug("Distance x,y = {}, {} with mrgid = {}".format(x, y, geom.mrgid))
        # quick check that the geom has been indexed
        mrgids = list(self.mrgids_info.keys())
        if geom.mrgid not in mrgids:
            # corner case
            # this should only happen for a zone that hasn't been indexed at all,
            # so we don't know how far the cell is from this zone
            logger.error("The passed geometry hasn't been indexed")
            logger.error("Fallback to heavy distance calculation")
            return geom.distance(x, y)

        mrgid_info = self.mrgids_info[geom.mrgid]
        # return early since the cell is within the zone
        within = mrgid_info.within
        if within:
            logger.debug("Case 1: returning 0")
            return 0.0

        # case 2 return the exact distance
        intersect = mrgid_info.intersect
        if intersect:
            logger.debug("Case 2: Computing the distance")
            return geom.distance(x, y)

        # case 3: return an estimation
        logger.debug("Case 3: Returning an estimate of the distance")
        return max(mrgid_info.corner_distances)

    def merge(self, other):
        """Assumint the mrgids set are disjoints"""
        self.mrgids_info.update(other.mrgids_info)


class SesameIndex:

    def __init__(self, gml_files, cell_size=1, **kwargs):
        """
        Index the geometry by points on a grid

        Args:
        geometries (list): the list of geometries to index (as given by
            load_geometry)
        """

        self.index = {}
        self.cell_size = cell_size

        logger.debug(gml_files)
        geometries = []
        for f in gml_files:
            geometry = SesameGeometry.from_gml_file(f, **kwargs)
            if geometry is not None:
                geometries.append(geometry)

        # create the index
        X = np.arange(-90.0, 90.0, cell_size)
        Y = np.arange(-180.0, 180.0, cell_size)

        # First pass, build the list points and their associated closest mrgids
        _index = defaultdict(list)
        for x in X:
            for y in Y:
                logging.debug("(x, y) = (%s, %s)" % (x, y))
                m = sys.maxsize
                mins = []
                for g in geometries:
                    # we store all the distances to all zones
                    d = distance(x, y, g)
                    _index[(x, y)].append((g, d))

                logger.info("(%s,%s) -> %s" % (x, y, _index[(x,y)]))

        # second pass, build the individual cells with some precomputed information
        for k, v in _index.items():
            x, y = k
            logging.debug("building cell for (x, y) = (%s, %s)" % (x, y))
            cx0, cy0, cx1, cy1, cx2, cy2, cx3, cy3 = SesameIndex.coord_corners(x, y, cell_size)
            ix0, iy0, ix1, iy1, ix2, iy2, ix3, iy3 = SesameIndex.index_corners(x, y, cell_size)
            c = IndexedCell().add_corner(cx0, cy0, _index[(ix0, iy0)])\
                             .add_corner(cx1, cy1, _index[(ix1, iy1)])\
                             .add_corner(cx2, cy2, _index[(ix2, iy2)])\
                             .add_corner(cx3, cy3, _index[(ix3, iy3)])\
                             .finalize()
            # recording the cell in the index
            self.index[k]  = c


    @staticmethod
    def coord_corners(x, y, cell_size):
        """x, y is the index of a cell (bottom left)"""
        x0 = x
        y0 = y
        x1 = x0 + cell_size
        y1 = y0
        x2 = x1
        y2 = y0 + cell_size
        x3 = x0
        y3 = y2
        return x0, y0, x1, y1, x2, y2, x3, y3

    @staticmethod
    def index_corners(x, y, cell_size):
        """x, y is the index of a cell (bottom left)"""
        x0 = x
        y0 = y
        x1 = ((x + 90) + cell_size) % 180 - 90
        y1 = y0
        x2 = x1
        y2 = ((y + 180) + cell_size) % 360 - 180
        x3 = x0
        y3 = y2
        return x0, y0, x1, y1, x2, y2, x3, y3

    def get_cell(self, x, y):
        index_x = (math.floor(x / self.cell_size) * self.cell_size + 90) % 180 - 90
        index_y = (math.floor(y / self.cell_size) * self.cell_size + 180) % 360 - 180
        logger.debug("Cell index = ({}, {})".format(index_x, index_y))
        return self.index[index_x, index_y]

    def distance(self, x, y, geom):
        cell = self.get_cell(x, y)
        return cell._distance(x, y, geom)

    def merge(self, other):
        """Assumption: the two indexes have been built on the same grid but not the same zones.

        side effect: this changes the current index by augmenting with the zones from the other index
        """
        for k, cells in self.index.items():
            self.index[k].merge(other.index[k])
        return self


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


def intersect(x1, y1, x2, y2, geometry):
    return geometry.intersect(x1, y1, x2, y2)


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

import json
import geojson
import shapely.geometry
from aether.base.placeholder.PlaceholderPolygon import PlaceholderPolygon

class AEPolygon(shapely.geometry.Polygon):
    """An object to make latlng/lnglat polygons easier. All platform operations are written to use AEPolygon objects, so
    as to not confuse latitude/longitude order using third-party systems with varying conventions.

    To quote from Stack Overflow:

    EPSG:4326 specifically states that the coordinate order should be latitude, longitude. Many software packages still
    use longitude, latitude ordering. This situation has wreaked unimaginable havoc on project deadlines and programmer
    sanity.
    """

    _object_type_name = "AEPolygon"

    # TODO(astrorobotic): Should refactor back to PlaceholderPolygon. Without altering user interface. Factory?
    def __init__(self, coordinates=None, holes=None):
        if coordinates is None:
            super(AEPolygon, self).__init__()
            self._is_placeholder = True
        else:
            super(AEPolygon, self).__init__(coordinates, holes=holes)
            self._is_placeholder = False

    def __repr__(self):
        return "AEPolygon()"

    def __str__(self):
        return "AEPolygon(lats={}, lngs={})".format(self.lats(), self.lngs())

    def lats(self):
        """Returns the coordinate latitude values as an array."""
        return [x for x in self.exterior.coords.xy[0]]

    def lngs(self):
        """Returns the coordinate longitude values as an array."""
        return [x for x in self.exterior.coords.xy[1]]

    def latlngs(self):
        """Returns the coordinate latitude-longitude values as an Nx2 array."""
        return map(list, zip(*[self.lats(), self.lngs()]))

    def lnglats(self):
        """Returns the coordinate longitude-latitude values as an Nx2 array."""
        return map(list, zip(*[self.lngs(), self.lats()]))


    # Questionably valuable methods. Perhaps should remove.
    @staticmethod
    def _is_string(s):
        return isinstance(s, str) or isinstance(s, unicode)

    @staticmethod
    def _str_to_arr(s):
        return json.loads(s)

    def from_lats_and_lngs(self, lats, lngs):
        """Loads a polygon using coordinate longitude and latitude values."""
        if AEPolygon._is_string(lats):
            lats = AEPolygon._str_to_arr(lats)
        if AEPolygon._is_string(lngs):
            lngs = AEPolygon._str_to_arr(lngs)
        return AEPolygon(map(list, zip(lats, lngs)))

    def from_latlngs(self, latlngs):
        """Loads a polygon using coordinate longitude and latitude values."""
        if AEPolygon._is_string(latlngs):
            latlngs = AEPolygon._str_to_arr(latlngs)
        return AEPolygon(latlngs)

    def from_lnglats(self, lnglats):
        """Loads a polygon using coordinate longitude and latitude values."""
        if AEPolygon._is_string(lnglats):
            lnglats = AEPolygon._str_to_arr(lnglats)
        return AEPolygon([[p[1],p[0]] for p in lnglats])

    # A tuple ordered (left, bottom, right, top)
    def from_bounds(self, bounds):
        """Loads a polygon using coordinate boundaries as a 4-tuple: (western longitude, southern latitude, eastern longitude, northern latitude)."""
        lats = [bounds[1], bounds[1], bounds[3], bounds[3], bounds[1]]
        lngs = [bounds[0], bounds[2], bounds[2], bounds[0], bounds[0]]
        return AEPolygon().from_lats_and_lngs(lats, lngs)

    # A tuple ordered (left, bottom, right, top)
    def to_bounds(self):
        """Returns a polygon coordinate boundaries as a 4-tuple: (western longitude, southern latitude, eastern longitude, northern latitude)."""
        return [min(self.lngs()), min(self.lats()), max(self.lngs()), max(self.lats())]

    def to_latlngs(self):
        if self._is_placeholder:
            return "{polygon_latlngs}"
        return map(list, zip(*[self.lats(), self.lngs()]))

    def to_lnglats(self):
        return map(list, zip(*[self.lngs(), self.lats()]))

    def to_latlng_bounds(self):
        bounds_dict = dict(
            north_lat=max(self.lats()),
            south_lat=min(self.lats()),
            east_lon=max(self.lngs()),
            west_lon=min(self.lngs()),
        )
        return bounds_dict

    def _to_dm_dict(self):
        dm = dict(
            lats=self.lats(),
            lngs=self.lngs()
        )
        return dm

    def _from_dm_dict(self, dm):
        return self.from_lats_and_lngs(dm["lats"], dm["lngs"])

    def to_geojson(self):
        return geojson.dumps(self)

    def from_geojson(self, s):
        o = geojson.loads(s)
        if o.type != "Polygon":
            print("WARNING: GeoJson is not a Polygon object. Returning None.")
            return None
        return AEPolygon().from_latlngs(o["coordinates"][0])

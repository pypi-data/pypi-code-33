import geojson
import aether as ae
import shapely.geometry

# TODO(): Does not handle multi-polygon GeoJSONs, e.g. with holes, in its serialization. AE Polygon does not as well.
class AEFeatureCollection(object):
    """An AEFeatureCollection is a list of AEPolygons"""

    _object_type_name = "AEFeatureCollection"

    def __init__(self):
        self._features = []

    def __repr__(self):
        return "AEFeatureCollection()"

    def __str__(self):
        return "AEFeatureCollection()"

    def addPolygon(self, polygon):
        if not isinstance(polygon, shapely.geometry.Polygon):
            print("WARNING: Argument is not a Polygon Object. Nothing added.")
            return self

        self._features.append(polygon)
        return self

    def to_geojson(self):
        return geojson.dumps(geojson.FeatureCollection(self._features))

    def from_geojson(self, s):
        o = geojson.loads(s)
        if o.type != "FeatureCollection":
            print("WARNING: GeoJson is not a FeatureCollection object. Returning None.")
            return None
        fc = AEFeatureCollection()
        for f in geojson.FeatureCollection(o)["features"]:
            fc.addPolygon(ae.AEPolygon(f["coordinates"][0]))
        return fc

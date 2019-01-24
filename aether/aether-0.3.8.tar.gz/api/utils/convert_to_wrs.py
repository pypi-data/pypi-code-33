import fiona
import shapely.geometry
import shapely.wkt
import logging
import dill

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class convert_to_wrs(object):
    """Class which performs conversion between latitude/longitude co-ordinates
        and Landsat WRS-2 paths and rows. Needs: http://landsat.usgs.gov/tools_wrs-2_shapefile.php"""

    @staticmethod
    def create_wrs_dill_file(wrs_file="static/WRS2_descending.shp",
                             wrs_dill_file="static/WRS2_descending.dill"):
        wrs = []
        for feature in fiona.open(wrs_file):
            wrs.append(
                dict(row=feature["properties"]["ROW"],
                     path=feature["properties"]["PATH"],
                     shape=shapely.geometry.shape(feature["geometry"])))
            if len(wrs) % 500 == 0:
                logger.info("Just added shape for Row {} and Path {}, number {}".format(
                    wrs[-1]["row"], wrs[-1]["path"], len(wrs)
                ))

        dill.dump(wrs, open(wrs_dill_file, 'wb'))

    def __init__(self, wrs_dill_file="static/WRS2_descending.dill"):
        self.wrs = dill.load(open(wrs_dill_file, "rb"))

    def get_wrs_from_latlng(self, lat, lng, limit_to_one=True):
        pt = shapely.geometry.Point(lng, lat)
        return self.get_wrs_from_shape(pt, limit_to_one=limit_to_one)

    def get_wrs_from_coords(self, coordinates, limit_to_one=True):
        c = list(map(list, zip(*coordinates)))
        coordinates = list(map(list, zip(*[c[1], c[0]])))
        shape = shapely.geometry.Polygon(coordinates)
        return self.get_wrs_from_shape(shape, limit_to_one=limit_to_one)

    def get_wrs_from_shape(self, shape, limit_to_one=True):
        """Get the Landsat WRS-2 path and row for the given
        latitude and longitude co-ordinates.
        Returns a list of dicts, as some points will be in the
        overlap between two (or more) landsat scene areas:
        [{path: 202, row: 26}, {path:186, row=7}]
        """

        import time
        s = time.time()
        if limit_to_one:
            res = next([w["path"], w["row"]] for w in self.wrs if shape.within(w["shape"]))
        else:
            res = []
            [res.append([w["path"], w["row"]]) for w in self.wrs if shape.within(w["shape"])]
        logger.info("Search time: {}".format(time.time()-s))
        return res

# coordinates = [[32.18061700462063, -116], [32.18061700462063, -115.96387659907587], [32.216740405544755, -115.96387659907587], [32.216740405544755, -116], [32.18061700462063, -116]]
# print(convert_to_wrs().get_wrs_from_coords(coordinates))
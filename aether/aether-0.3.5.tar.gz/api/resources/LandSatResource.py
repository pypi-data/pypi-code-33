from api.base.SearchResourceResourceBase import SearchResourceResourceBase
from api.gis.geotiff_search_handler import geotiff_search_handler
from aether_shared.utilities.user_api_utils import user_api_utils
from aether.proto.api_pb2 import SpacetimeBuilder, RasterLayer
import aether.aetheruserconfig as cfg
from api.utils.convert_to_wrs import convert_to_wrs
from google.protobuf import json_format

import json

import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class LandSatResource(SearchResourceResourceBase):

    _resource_name = "landsat"

    _meta_search_config = dict(
        metadata_table_id = "bigquery-public-data.cloud_storage_geo_index.landsat_index",
        exclude_parameters_from_metadata_search = ["bands"],
        additional_where_conditions = [], # [ "(spacecraft_id='LANDSAT_8')" ],
        serverside_type_maps = {}, # dict(date_acquired="TIMESTAMP({})")
        resource_name = _resource_name,
    )

    _query_parameters = cfg.resources[_resource_name]["_query_parameters"]

    _band_replacement = dict(
        LANDSAT_4 = dict(QA="BQA", ULTRA_BLUE=None, BLUE="B1", GREEN="B2", RED="B3", NIR="B4", SWIR1="B5", SWIR2="B7", PANCHROMATIC=None, CIRRUS=None, TIRS1="B6", TIRS2=None),
        LANDSAT_5 = dict(QA="BQA", ULTRA_BLUE=None, BLUE="B1", GREEN="B2", RED="B3", NIR="B4", SWIR1="B5", SWIR2="B7", PANCHROMATIC=None, CIRRUS=None, TIRS1="B6", TIRS2=None),
        LANDSAT_7 = dict(QA="BQA", ULTRA_BLUE=None, BLUE="B1", GREEN="B2", RED="B3", NIR="B4", SWIR1="B5", SWIR2="B7", PANCHROMATIC="B8", CIRRUS=None, TIRS1="B6", TIRS2=None),
        LANDSAT_8 = dict(QA="BQA", ULTRA_BLUE="B1", BLUE="B2", GREEN="B3", RED="B4", NIR="B5", SWIR1="B6", SWIR2="B7", PANCHROMATIC="B8", CIRRUS="B9", TIRS1="B10", TIRS2="B11"),
    )

    def __init__(self, global_objects):
        self.wrs_search_util = convert_to_wrs()
        self._geotiff_search_handler = geotiff_search_handler(global_objects, logger)
        super(LandSatResource, self).__init__(global_objects, self._query_parameters, logger)

    def search(self, parameter_values, polygon):
        response = SpacetimeBuilder()
        response.polygon.latlngs = json.dumps(polygon.to_latlngs())

        bands = parameter_values["bands"]

        # The LandSat WRS2 Tiles are not aligned with Lat-Lng. As a result, the LatLng bounds in Google BigQuery can
        # retrieve tiles that have masked black portions. This searches the shapefiles of the WRS2 Tiles, and then
        # converts a search for the polygon in BigQuery into a search for the PathRow.
        # This is most likely a common problem across almost all Tiff files of data not on WGS84 alignment and a general
        # solution will need to be found.
        pathrows = self.wrs_search_util.get_wrs_from_coords(polygon.to_latlngs(), limit_to_one=True)
        if len(pathrows) == 0:
            return response
        parameter_values["wrs_path"] = pathrows[0]
        parameter_values["wrs_row"] = pathrows[1]

        # Notice that polygon is set to None.
        rows = self._geotiff_search_handler.query_resource_meta_with_polygon(
            parameter_values, None, self._query_parameters, self._meta_search_config)

        for row in rows:
            metadata = {n: row._xxx_values[i] for n, i in row._xxx_field_to_index.iteritems()}
            timestamp = row["date_acquired"]
            resource_name = metadata["spacecraft_id"]

            base_url = row["base_url"]
            base_file = row["base_url"].split("/")[-1]

            bands_on_serverside = self._bands_in_serverside_terms(resource_name, bands)
            bands_to_process = ["{}/{}_{}.TIF".format(base_url, base_file, b) for b in bands_on_serverside]

            raster_layers = []
            for b_i in range(len(bands)):
                r = RasterLayer()
                r.download_stub = bands_to_process[b_i]
                r.download_url = user_api_utils.gs_stub_to_url(bands_to_process[b_i])
                r.timestamp = timestamp
                r.canonical_name = "{}_{}".format(resource_name, bands[b_i])
                raster_layers.append(r)
            response.timestamps[timestamp].layers.extend(raster_layers)
            response.timestamps[timestamp].properties["resource_metadata"] = json.dumps(metadata)

        return json_format.MessageToJson(response), 200

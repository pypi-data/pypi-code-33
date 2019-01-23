from api.base.SearchResourceResourceBase import SearchResourceResourceBase
from api.gis.geotiff_search_handler import geotiff_search_handler
from aether_shared.utilities.user_api_utils import user_api_utils
import aether.aetheruserconfig as cfg
from aether.proto.api_pb2 import SpacetimeBuilder, RasterLayer
from google.protobuf import json_format

import json

import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# Improvements
# TODO(davidbernat): Add QA Band data, add Weather data!

class SentinelResource(SearchResourceResourceBase):

    _resource_name = "sentinel"

    _meta_search_config = dict(
        metadata_table_id = "bigquery-public-data.cloud_storage_geo_index.sentinel_2_index",
        exclude_parameters_from_metadata_search = ["bands"],
        additional_where_conditions = [],
        serverside_type_maps = dict(
            date_acquired="sensing_time",
            cloud_cover="CAST(cloud_cover as FLOAT64)/100.0"),
        resource_name = _resource_name,
    )

    _band_replacement = dict(
        SENTINEL_2A = dict(COASTAL_AEROSOL="B01", BLUE="B02", GREEN="B03", RED="B04", VEG_RED_EDGE1="B05", VEG_RED_EDGE2="B06",
                           VEG_RED_EDGE3="B07", NIR="B08", NARROW_NIR="B8A", WATER_VAPOR="B09", CIRRUS="B10", SWIR1="B11", SWIR2="B12"),
    )

    _query_parameters = cfg.resources[_resource_name]["_query_parameters"]

    def __init__(self, global_objects):
        self._geotiff_search_handler = geotiff_search_handler(global_objects, logger)
        super(SentinelResource, self).__init__(global_objects, self._query_parameters, logger)

    def search(self, parameter_values, polygon):
        bands = parameter_values["bands"]
        rows = self._geotiff_search_handler.query_resource_meta_with_polygon(
            parameter_values, polygon, self._query_parameters, self._meta_search_config)

        response = SpacetimeBuilder()
        response.polygon.latlngs = json.dumps(polygon.to_latlngs())
        for row in rows:
            metadata = {n: row._xxx_values[i] for n, i in row._xxx_field_to_index.iteritems()}

            # These five lines are different than LandSatAPI
            timestamp = row["sensing_time"]
            resource_name = "SENTINEL_2A"
            base_url = "{}/GRANULE/{}/IMG_DATA/".format(row["base_url"], row["granule_id"])

            bands_on_serverside = self._bands_in_serverside_terms(resource_name, bands)
            # Old format Naming Convention for Sentinel-2 Level-1C products generated before the 6th of December, 2016
            # See: https://earth.esa.int/web/sentinel/user-guides/sentinel-2-msi/naming-convention
            if timestamp < "2016-12-06":
                base_file = "_".join(row["granule_id"].split("_")[:-1])
                bands_to_process = ["{}{}_{}.jp2".format(base_url, base_file, b) for b in bands_on_serverside]
            else:
                datatake_date = row["datatake_identifier"].split("_")[1]
                bands_to_process = ["{}T{}_{}_{}.jp2".format(base_url, row["mgrs_tile"], datatake_date, b) for b in bands_on_serverside]

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

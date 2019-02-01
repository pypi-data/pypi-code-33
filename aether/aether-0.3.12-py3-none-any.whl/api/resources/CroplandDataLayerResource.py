from api.base.SearchResourceResourceBase import SearchResourceResourceBase
from api.gis.geotiff_search_handler import geotiff_search_handler
from aether.proto.api_pb2 import RasterLayer
from aether_shared.utilities.user_api_utils import user_api_utils
from aether.proto.api_pb2 import SpacetimeBuilder
import aether.aetheruserconfig as cfg
from google.protobuf import json_format
from dbfread import DBF
import json

import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class CroplandDataLayerResource(SearchResourceResourceBase):

    _resource_name = "cropland_data_layer"

    _meta_search_config = dict(
        metadata_table_id = "aether-185123.ae_data_platform_resource_metadata_dataset.cropland_data_layer",
        exclude_parameters_from_metadata_search = [],
        additional_where_conditions = [], # [ "(spacecraft_id='LANDSAT_8')" ],
        serverside_type_maps = {}, # dict(date_acquired="TIMESTAMP({})")
        resource_name = _resource_name,
    )

    _query_parameters = cfg.resources[_resource_name]["_query_parameters"]

    def __init__(self, global_objects):
        self._geotiff_search_handler = geotiff_search_handler(global_objects, logger)
        super(CroplandDataLayerResource, self).__init__(global_objects, self._query_parameters, logger)

    def search(self, parameter_values, polygon):
        rows = self._geotiff_search_handler.query_resource_meta_with_polygon(
            parameter_values, polygon, self._query_parameters, self._meta_search_config)

        response = SpacetimeBuilder()
        response.polygon.latlngs = json.dumps(polygon.to_latlngs())
        for row in rows:
            metadata = {n: row._xxx_values[i] for n, i in row._xxx_field_to_index.iteritems()}
            timestamp = row["year"]
            resource_name = metadata["resource_name"]
            band = metadata["resource_filestub"]

            r = RasterLayer()
            r.download_stub = band
            r.download_url = user_api_utils.gs_stub_to_url(band)
            r.timestamp = timestamp
            r.canonical_name = "{}_{}".format(resource_name, band)

            # Retrieve the color table for this resource. It is associated_filestub index 0.
            color_table_stub = json.loads(row["resource_associated_filestubs"].replace("\'", "\""))[0]
            crop_names, color_table = self._read_crop_registry_file(self._global_objects.filemanager().retrieve_stub(color_table_stub))

            r.color_table = json.dumps(color_table)
            r.properties["crop_names"] = json.dumps(crop_names)

            response.timestamps[timestamp].layers.extend([r])
            response.timestamps[timestamp].properties["resource_metadata"] = json.dumps(metadata)
        return json_format.MessageToJson(response), 200


    # The CDL Meta file, which contains conversion from number to crop name and crop color, is different for every year.
    @staticmethod
    def _read_crop_registry_file(crop_registry_file):
        table = DBF(crop_registry_file.name, load=True)
        crop_types = table.records

        crop_names = {crop_types[i]['VALUE']: crop_types[i]['CLASS_NAME'] for i in range(len(crop_types))}

        # There are some entries with None, so those need to be excluded.
        exclude = []
        [exclude.append(i) for i in range(len(crop_types)) if not isinstance(crop_types[i]['RED'], float)]
        [exclude.append(i) for i in range(len(crop_types)) if not isinstance(crop_types[i]['GREEN'], float)]
        [exclude.append(i) for i in range(len(crop_types)) if not isinstance(crop_types[i]['BLUE'], float)]
        [exclude.append(i) for i in range(len(crop_types)) if not isinstance(crop_types[i]['OPACITY'], float)]

        color_table = {int(crop_types[i]['VALUE']):
                           (int(255. * crop_types[i]['RED']),
                            int(255. * crop_types[i]['GREEN']),
                            int(255. * crop_types[i]['BLUE']),
                            int(255. * crop_types[i]['OPACITY'])) for i in range(len(crop_types)) if i not in exclude}
        for i in set(exclude):
            color_table[int(i)] = (0,0,0,0)
        return crop_names, color_table






from api.gis.geotiff_transforms_handler import geotiff_transforms_handler
from aether import SpacetimeBuilder
from aether_shared.utilities.user_api_utils import user_api_utils
from aether_shared.utilities.firebase_utils import firebase_utils
from aether_shared.utilities.api_utils import api_utils
from flask_restful import reqparse
from flask import request
from flask_restful import Resource
from aether.dataobjects.AEPolygon import AEPolygon
import aether.proto.api_pb2 as api_pb2
from google.protobuf import json_format
import hashlib
import pyproj
import json

import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ClipAndShipResource(Resource):

    def __init__(self, global_objects):
        self.lazy_cache = True
        self._global_objects = global_objects
        self._geotiff_transforms_handler = geotiff_transforms_handler(global_objects, logger)

    def post(self):
        parser = reqparse.RequestParser(bundle_errors=True)
        parser.add_argument('uuid', type=str, required=True, location='json')
        parser.add_argument('builder', type=str, required=True, location='json')
        parser.add_argument('projection', type=str, required=True, location='json')
        args = parser.parse_args()

        uuid = args["uuid"]
        if not self._global_objects.authenticator().is_authorized_user(uid=uuid):
            return api_utils.log_and_return_status(
                "Unauthorized UUID {}".format(uuid), 401, request, logger)

        builder = firebase_utils.verify_pb(args["builder"], SpacetimeBuilder(), return_pb_if_valid=True)
        if builder is None:
            return api_utils.log_and_return_status(
                "Request contains improperly formed builder object for builder_type.", 400, request, logger)

        try:
            projection = json.loads(args["projection"])
            if projection is not None:
                pyproj.Proj(projection)
        except:
            return api_utils.log_and_return_status(
                "Request contains improperly formed projection {}".format(args["projection"]), 400, request, logger)

        try:
            response, code = self.crop(builder, uuid, projection)
            return api_utils.log_and_return_status(response, code, request, logger)
        except Exception:
            return api_utils.log_and_return_status("ClipAndShipResource failed during operation.", 500, request, logger, exc_info=True)

    def crop(self, builder, uuid, projection):
        """Applies a cropping of shape Polygon to Filestubs listed in the request of type SpacetimeBuilder. """
        polygon = AEPolygon().from_latlngs(builder.polygon.latlngs)

        response = api_pb2.SpacetimeBuilder()
        for timestamp in builder.timestamps.keys():
            moment_in_time = builder.timestamps[timestamp]
            polygon_hash = hashlib.md5(str(polygon.to_latlngs()).encode()).hexdigest()

            raster_layers = []
            for layer_i in range(len(moment_in_time.layers)):
                layer = moment_in_time.layers[layer_i]

                destination_stub = "user://{uuid}/{polygon_hash}_{timestamp}_{resource_name}.tif".format(
                    uuid=uuid,
                    polygon_hash=polygon_hash,
                    timestamp=layer.timestamp,
                    resource_name=layer.canonical_name
                )

                try:
                    # Lazy cache
                    if not (self.lazy_cache and self._global_objects.filemanager().stub_exists(destination_stub)):
                        self._geotiff_transforms_handler.crop_raster_layer(layer, polygon, projection, destination_stub)
                    else:
                        logger.info("Using lazy cache to retrieve without re-cropping: {}".format(destination_stub))

                    stub_url = user_api_utils.user_stub_to_signed_url(destination_stub)
                    layer.download_url = stub_url
                    layer.download_stub = destination_stub
                    layer.canonical_name = "{polygon_hash}_{resource_name}".format(
                        polygon_hash=polygon_hash, resource_name=layer.canonical_name)

                    raster_layers.append(layer)
                except Exception:
                    return api_utils.log_and_return_status("_crop_image_object failed on RasterLayer: {} {}".format(timestamp, layer), 500, request, logger, exc_info=True)
            response.timestamps[timestamp].layers.extend(raster_layers)
            response.timestamps[timestamp].properties["resource_metadata"] =\
                builder.timestamps[timestamp].properties["resource_metadata"]

        return json_format.MessageToJson(response), 200

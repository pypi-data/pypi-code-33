from __future__ import absolute_import
from api.gis.geotiff_transforms_handler import geotiff_transforms_handler
# from api.functions.RasterLayerClipAndShip.main import raster_layer_clip_and_ship
from aether import SpacetimeBuilder
from aether_shared.utilities.user_api_utils import user_api_utils
from aether_shared.utilities.firebase_utils import firebase_utils
from aether_shared.utilities.api_utils import api_utils
from flask_restful import reqparse
from flask import request, Flask
from flask_restful import Resource
from aether.dataobjects.AEPolygon import AEPolygon
import aether.proto.api_pb2 as api_pb2
from google.protobuf import json_format
import hashlib
import pyproj
import json
import requests
import aether as ae

from multiprocessing.dummy import Pool

import logging
from six.moves import range
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class function_wrapper_clip_and_ship(object):

    def __init__(self, n_threads=100, mode="kubernetes"):
        self._mode = mode
        self._n_threads = n_threads
        self._pool = Pool(n_threads)
        self.is_local = (mode == "local")

    def pool(self):
        return self._pool

    def request(self, uuid, layer, polygon, projection, destination_stub):
        if self._mode == "kubernetes":
            return self.make_request(uuid, layer, polygon, projection, destination_stub, is_cloud_function=False)
        if self._mode == "function":
            return self.make_request(uuid, layer, polygon, projection, destination_stub, is_cloud_function=True)

    def make_request(self, uuid, layer, polygon, projection, destination_stub, is_cloud_function=False):
        if is_cloud_function:
            region = "us-central1-aether-185123"
            function_name = "raster_layer_clip_and_ship"
            url = "https://{}.cloudfunctions.net/{}".format(region, function_name)
        else:
            hostport = ae.GlobalConfig.hostport
            entry = "/api/v1.0/sky/_raster_layer_clip_and_ship/"
            url = "http://{hostport}{entry}".format(hostport=hostport, entry=entry)

        headers = {'Content-Transfer-Encoding': 'base64'}
        data = dict(
            uuid=uuid,
            polygon=json.dumps(polygon.to_latlngs()),
            raster_layer = json_format.MessageToJson(layer),
            projection_crs = json.dumps(projection),
            destination_stub=destination_stub
        )
        op = "Cloud Function" if is_cloud_function else "Kubernetes Service"
        logger.info("Making Request to {}: {} \n Request: {}".format(op, url, str(data)[:1000]))

        kwargs = dict(json=data, headers=headers)
        return self.pool().apply_async(requests.post, (url,), kwargs)

    def run_local(self, uuid, layer, polygon, projection, destination_stub, filemanager, logger):
        logger.info("Running Crop Locally: {}".format([layer, polygon, projection, destination_stub]))
        geotiff_transforms_handler.crop_raster_layer(layer, polygon, projection, destination_stub,
                                                     filemanager, logger)



class ClipAndShipResource(Resource):

    def __init__(self, global_objects):
        self.lazy_cache = True
        self._global_objects = global_objects

    def post(self):
        parser = reqparse.RequestParser(bundle_errors=True)
        parser.add_argument('uuid', type=str, required=True, location='json')
        parser.add_argument('builder', type=str, required=True, location='json')
        parser.add_argument('projection', type=str, required=True, location='json')
        parser.add_argument('mode', type=str, required=True, default="local", location='json')
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
            mode = args["mode"]
            response, code = self.crop(builder, uuid, projection, mode)
            return api_utils.log_and_return_status(response, code, request, logger)
        except Exception:
            return api_utils.log_and_return_status("ClipAndShipResource failed during operation.", 500, request, logger, exc_info=True)

    def crop(self, builder, uuid, projection, mode):
        """Applies a cropping of shape Polygon to Filestubs listed in the request of type SpacetimeBuilder. """
        polygon = AEPolygon().from_latlngs(builder.polygon.latlngs)

        # helper = function_wrapper_clip_and_ship(mode="kubernetes")
        helper = function_wrapper_clip_and_ship(mode=mode)

        layers_to_compile = {}
        futures = []
        for timestamp in builder.timestamps.keys():
            moment_in_time = builder.timestamps[timestamp]
            polygon_hash = hashlib.md5(str(polygon.to_latlngs()).encode()).hexdigest()

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
                    if timestamp not in layers_to_compile:
                        layers_to_compile[timestamp] = {}
                    layers_to_compile[timestamp][layer_i] = destination_stub

                    stub_exists = self._global_objects.filemanager().stub_exists(destination_stub)
                    if self.lazy_cache and stub_exists:
                        logger.info("Using lazy cache to retrieve without re-cropping: {}".format(destination_stub))
                    else:
                        if helper.is_local:
                            helper.run_local(uuid, layer, polygon, projection, destination_stub,
                                             self._global_objects.filemanager(), logger)
                        else:
                            futures.append(helper.request(uuid, layer, polygon, projection, destination_stub))
                except Exception:
                    return api_utils.log_and_return_status("_crop_raster_layer failed during operation.", 500, request, logger)

        # If not running locally, check that all the async files are finished and in their locations.
        if not helper.is_local:
            for future in futures:
                response = future.get()
                if not response.ok:
                    return api_utils.log_and_return_status("_crop_raster_layer failed during operation: {}".format(future), 500, request, logger)

        response = api_pb2.SpacetimeBuilder()
        for timestamp in builder.timestamps.keys():
            moment_in_time = builder.timestamps[timestamp]
            raster_layers = []
            for layer_i in range(len(moment_in_time.layers)):
                layer = moment_in_time.layers[layer_i]
                destination_stub = layers_to_compile[timestamp][layer_i]

                stub_url = user_api_utils.user_stub_to_signed_url(destination_stub)
                layer.download_url = stub_url
                layer.download_stub = destination_stub
                layer.canonical_name = "{resource_name}".format(resource_name=layer.canonical_name)
                raster_layers.append(layer)
            response.timestamps[timestamp].layers.extend(raster_layers)
            response.timestamps[timestamp].properties["resource_metadata"] =\
                builder.timestamps[timestamp].properties["resource_metadata"]

        return json_format.MessageToJson(response), 200

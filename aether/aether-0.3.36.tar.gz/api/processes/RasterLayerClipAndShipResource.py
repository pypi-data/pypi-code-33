from __future__ import absolute_import
from api.gis.geotiff_transforms_handler import geotiff_transforms_handler
from aether_shared.utilities.firebase_utils import firebase_utils
from aether_shared.utilities.api_utils import api_utils
from flask_restful import reqparse
from flask import request, Flask
from flask_restful import Resource
from aether.dataobjects.AEPolygon import AEPolygon
from aether.proto.api_pb2 import RasterLayer

import pyproj
import json

import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class RasterLayerClipAndShipResource(Resource):

    def __init__(self, global_objects):
        self._global_objects = global_objects

    def post(self):
        parser = reqparse.RequestParser(bundle_errors=True)
        parser.add_argument('uuid', type=str, required=True, location='json')
        parser.add_argument("polygon", type=str, required=True, location='json')
        parser.add_argument("raster_layer", type=str, required=True, location='json')
        parser.add_argument('projection_crs', type=str, required=True, location='json')
        parser.add_argument('destination_stub', type=str, required=True, location='json') # Required
        args = parser.parse_args()

        if not self._global_objects._authenticator.is_authorized_user(uid=args["uuid"]):
            return api_utils.log_and_return_status(
                "Unauthorized UUID {}".format(args["uuid"]), 401, request, logger)

        try:
            polygon = AEPolygon().from_latlngs(args["polygon"])
        except Exception:
            return api_utils.log_and_return_status(
                "Request has incorrectly formed polygon.", 401, request, logger, exc_info=True)

        try:
            projection_crs = json.loads(args["projection_crs"])
            if projection_crs is not None:
                pyproj.Proj(projection_crs)
        except:
            return api_utils.log_and_return_status(
                "Request contains improperly formed projection {}".format(args["projection_crs"]), 400, request, logger)

        raster_layer = firebase_utils.verify_pb(args["raster_layer"], RasterLayer(), return_pb_if_valid=True)
        if raster_layer is None:
            return api_utils.log_and_return_status(
                "Request contains improperly formed builder object for builder_type.", 400, request, logger)

        destination_stub = args["destination_stub"]

        # Raise any errors back directly.
        geotiff_transforms_handler.crop_raster_layer(raster_layer, polygon, projection_crs, destination_stub,
                                                     self._global_objects.filemanager(), logger)




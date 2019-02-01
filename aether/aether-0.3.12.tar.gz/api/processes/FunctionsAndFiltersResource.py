import aether as ae
from aether.proto.api_pb2 import SpacetimeBuilder, BytesTransmission, BuildtimeOperation
from aether.dataobjects.Spacetime import Spacetime as SpacetimeDo
from aether.sky_utils import sky_utils
from flask import request
from aether_shared.utilities.user_api_utils import user_api_utils
from flask_restful import reqparse
import time, hashlib, tempfile
from google.protobuf import json_format
import json
# from RestrictedPython import compile_restricted
# from RestrictedPython import safe_globals, utility_builtins
# import inspect
import base64

from aether_shared.utilities.firebase_utils import firebase_utils
from aether_shared.utilities.api_utils import api_utils
from api.base.PostMethodResourceBase import PostMethodResourceBase

import logging
logger = logging.getLogger(__name__)

class FunctionsAndFiltersResource(PostMethodResourceBase):

    _post_methods = dict(
        FilterFunction="FilterFunction",
    )

    def __init__(self, global_objects):
        self._global_objects = global_objects
        super(FunctionsAndFiltersResource, self).__init__(global_objects, logger)

    def FilterFunction(self, request):
        """Applies a Filter Function to a SpacetimeBuilder"""
        parser = reqparse.RequestParser(bundle_errors=True)
        parser.add_argument('uuid', type=str, required=True, location='json')
        parser.add_argument('builder', type=str, required=True, location='json')
        parser.add_argument('filters', type=str, required=True, location='json')
        parser.add_argument('filters_args', type=str, required=True, location='json')
        parser.add_argument('polygon', type=str, required=False, default=None, location='json')
        args = parser.parse_args()

        builder = firebase_utils.verify_pb(args["builder"], SpacetimeBuilder(), return_pb_if_valid=True)
        if builder is None:
            return api_utils.log_and_return_status(
                "Request contains improperly formed builder object for builder_type.", 400, request, logger)

        try:
            if args["polygon"] is None:
                polygon = None
            else:
                polygon = ae.AEPolygon().from_latlngs(args["polygon"])
        except Exception:
            return api_utils.log_and_return_status(
                "Request has incorrectly formed polygon.", 401, request, self._logger, exc_info=True)

        try:
            filter_args = json.loads(args["filters_args"])
        except Exception:
            return api_utils.log_and_return_status(
                "Request has incorrectly json'd filters args.", 401, request, self._logger, exc_info=True)

        try:
            filter_strs = json.loads(args["filters"])
        except Exception:
            return api_utils.log_and_return_status(
                "Request has incorrectly json'd or serialized filters.", 401, request, self._logger, exc_info=True)

        timestamps = list(sorted(builder.timestamps.keys()))
        will_keep = [True] * len(timestamps)
        if len(filter_strs) != 0 and len(timestamps) != 0:
            # TODO(astrorobotic): This should *absolutely not* be attributed to the UUID. It should be admin.
            uuid = args["uuid"]
            ae.GlobalConfig.set_user(uuid)
            with ae.SkySession() as sky:
                for op_i, filter_string in enumerate(filter_strs):
                    try:
                        btop = json_format.Parse(filter_string, BuildtimeOperation())
                        op = self.deserialize_function(btop.serialized_func)
                    except:
                        return api_utils.log_and_return_status(
                            "Request contains improperly formed BuildtimeOperation {} bytestring in filter.".format(op_i),
                            400, request, logger, exc_info=True)
                    try:
                        to_keep = op(sky, builder, polygon=polygon, **filter_args[op_i])
                    except:
                        return api_utils.log_and_return_status(
                            "BuildtimeOperation {} in builder failed during operation.".format(op_i),
                            422, request, logger, exc_info=True)
                    logger.info("Filter {} returned {}".format(op_i, to_keep))
                    will_keep = [will_keep[i] * to_keep[i] for i in range(len(will_keep))]
                    logger.info("New will_keep values {}".format(will_keep))

            for ts_i in range(len(will_keep)):
                if not will_keep[ts_i]:
                    del builder.timestamps[timestamps[ts_i]]
        return json_format.MessageToJson(builder), 200

    @staticmethod
    def deserialize_function(s):
        s = base64.urlsafe_b64decode(s)
        y = compile(s, "<inline>", "exec")
        loc = {}
        exec(y, None, loc)
        return loc[list(loc.keys())[0]]

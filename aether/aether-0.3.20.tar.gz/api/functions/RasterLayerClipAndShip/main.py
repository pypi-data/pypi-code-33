from __future__ import absolute_import
from flask_restful import reqparse
from ._google_firebase import google_firebase
from google.protobuf import json_format
from ._api_pb2 import ErrorMessage, RasterLayer
from google.protobuf.message import DecodeError
from ._geotiff_transforms_handler import geotiff_transforms_handler
from ._google_cloud_storage_io import google_cloud_storage_io
from ._universal_filemanager import universal_filemanager

import aether as ae
import traceback
import sys
import json
import pyproj

import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

_authenticator = google_firebase()
_filemanager = universal_filemanager(google_cloud_storage_io())


def _create_error_message(error_type, message, trace, code, pb=None):
    # Compile Error Information
    e = ErrorMessage()
    if error_type is not None:
        e.name = type(message).__name__
        e.code = code
        e.message = message.message
        e.trace.extend(traceback.format_tb(trace))
        if pb is not None:
            e.accompanying_pb = pb.SerializeToString()
            e.accompanying_pb_name = type(pb).__name__
    return e

def _log_and_return_status(msg, code, request, logger, exc_info=False):
    error_type, message, trace = sys.exc_info()
    logger.info("{}: {:.10000} \n Request: {:.10000}".format(code, str(msg), str(request)), exc_info=exc_info)

    if error_type is not None:
        e = _create_error_message(error_type, message, trace, code, pb=None)
        return json_format.MessageToJson(e), code

    return msg, code



def _serialize_pb(pb):
    return json_format.MessageToJson(pb)

def _deserialize_pb(s, pb):
    return json_format.Parse(s, pb)

def _verify_pb(json_string, pb, return_pb_if_valid=False):
    try:
        pb = _deserialize_pb(json_string, pb)
        if return_pb_if_valid:
            return pb
        else:
            return True
    except DecodeError:
        if return_pb_if_valid:
            return None
        else:
            return False


def raster_layer_clip_and_ship(request):
    """HTTP Cloud Function.
    Args:
        request (flask.Request): The request object.
        <http://flask.pocoo.org/docs/1.0/api/#flask.Request>
    Returns:
        The response text, or any set of values that can be turned into a
        Response object using `make_response`
        <http://flask.pocoo.org/docs/1.0/api/#flask.Flask.make_response>.
    """

    parser = reqparse.RequestParser(bundle_errors=True)
    parser.add_argument('uuid', type=str, required=True, location='json')
    parser.add_argument("polygon", type=str, required=True, location='json')
    parser.add_argument("raster_layer", type=str, required=True, location='json')
    parser.add_argument('projection_crs', type=str, required=True, location='json')
    parser.add_argument('destination_stub', type=str, required=True, location='json') # Required
    args = parser.parse_args()

    if not _authenticator.is_authorized_user(uid=args["uuid"]):
        return _log_and_return_status(
            "Unauthorized UUID {}".format(args["uuid"]), 401, request, logger)

    try:
        polygon = ae.AEPolygon().from_latlngs(args["polygon"])
    except Exception:
        return _log_and_return_status(
            "Request has incorrectly formed polygon.", 401, request, logger, exc_info=True)

    try:
        projection_crs = json.loads(args["projection_crs"])
        if projection_crs is not None:
            pyproj.Proj(projection_crs)
    except:
        return _log_and_return_status(
            "Request contains improperly formed projection {}".format(args["projection_crs"]), 400, request, logger)

    raster_layer = _verify_pb(args["raster_layer"], RasterLayer(), return_pb_if_valid=True)
    if raster_layer is None:
        return _log_and_return_status(
            "Request contains improperly formed builder object for builder_type.", 400, request, logger)

    destination_stub = args["destination_stub"]

    # Raise any errors back directly.
    geotiff_transforms_handler.crop_raster_layer(raster_layer, polygon, projection_crs, destination_stub,
                                                 _filemanager, logger)




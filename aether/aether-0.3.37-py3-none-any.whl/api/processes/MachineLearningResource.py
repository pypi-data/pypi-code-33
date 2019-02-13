# from aether_shared.utilities.user_api_utils import user_api_utils
# from aether_shared.utilities.api_utils import api_utils
# from flask_restful import reqparse
# from flask import request
# from api.base.PostMethodResourceBase import PostMethodResourceBase
# from aether.dataobjects.AEPolygon import AEPolygon
# import aether.proto.api_pb2 as api_pb2
# from pygeotile.tile import Tile
# import numpy as np
# from aether.proto.api_pb2 import SpacetimeBuilder
# import hashlib
#
# from aether_shared.utilities.firebase_utils import firebase_utils
# import logging
# logging.basicConfig(level=logging.INFO)
# logger = logging.getLogger(__name__)
#
#
# # TODO(astrorobotic): Loading of models is not ThreadSafe wrt the Cloud. How do we handle that? Lock with NRT DB?
# # TODO(astrorobotic): Most likely model_id ought to be a general construct.
# # TODO(astrorobotic): Spacetime Builders need to be of the same size.
# # TODO(astrorobotic): Refactor ML model work into Aether User SDK
#
# class MachineLearningResource(PostMethodResourceBase):
#     """
#         The MachineLearningResource handles operations to train, save/load, infer, and test ML and ML-like models.
#
#         POST Train: Loads and trains the requested model if exists, creates and trains, otherwise.
#         POST UpdateApp: Updated a SkyApplication already in public usage.
#         """
#
#     _post_methods = dict(
#         Train="Train",
#         Infer="Infer",
#     )
#
#     def __init__(self, global_objects):
#         self._global_objects = global_objects
#         super(MachineLearningResource, self).__init__(global_objects, logger)
#
#     def Infer(self, request):
#         parser = reqparse.RequestParser(bundle_errors=True)
#         parser.add_argument('uuid', type=str, required=True, location='json')
#         parser.add_argument("model_id", type=str, required=False, location='json')
#         parser.add_argument("model_config", type=str, required=False, location='json')
#         args = parser.parse_args()
#
#
#     def Train(self, request):
#         parser = reqparse.RequestParser(bundle_errors=True)
#         parser.add_argument('uuid', type=str, required=True, location='json')
#         parser.add_argument("model_id", type=str, required=False, location='json')
#         parser.add_argument("model_config", type=str, required=False, location='json')
#         parser.add_argument('builder_x', type=str, required=True, location='json')
#         parser.add_argument('builder_y', type=str, required=True, location='json')
#         args = parser.parse_args()
#
#         builder_x = firebase_utils.verify_pb(args["builder_x"], SpacetimeBuilder(), return_pb_if_valid=True)
#         if builder_x is None:
#             return api_utils.log_and_return_status(
#                 "Request contains improperly formed builder object for builder_x.", 400, request, logger)
#
#         builder_y = firebase_utils.verify_pb(args["builder_y"], SpacetimeBuilder(), return_pb_if_valid=True)
#         if builder_y is None:
#             return api_utils.log_and_return_status(
#                 "Request contains improperly formed builder object for builder_y.", 400, request, logger)
#
#
#
#
#         try:
#             response, code = self.train_model(args["uuid"], )
#             api_utils.log_and_return_status(response, 200, request, logger)
#         except Exception:
#             return api_utils.log_and_return_status("MachineLearningResource failed during operation.", 500, request, logger, exc_info=True)
#
#     def inference(self, uuid, polygon, zoom):
#         """Applies an object detection algorithm over a set of tiles bound by the polygon."""
#
#         # Assume rectangular polygon right now.
#         min_x = np.min([Tile.for_latitude_longitude([p[0]],p[1], zoom).google[0] for p in polygon.latlngs()])
#         max_x = np.max([Tile.for_latitude_longitude([p[0]],p[1], zoom).google[0] for p in polygon.latlngs()])
#         min_y = np.min([Tile.for_latitude_longitude([p[0]],p[1], zoom).google[1] for p in polygon.latlngs()])
#         max_y = np.max([Tile.for_latitude_longitude([p[0]],p[1], zoom).google[1] for p in polygon.latlngs()])
#
#         for x in range(min_x, max_x + 1):
#             for y in range(min_y, max_y + 1):
#                 src = "https://mt0.google.com/vt/lyrs=s&?x={x}&y={y}&z={z}".format(x=x, y=y, z=zoom)
#
#
#         polygon = AEPolygon().from_latlngs(builder.polygon.latlngs)
#
#         response = api_pb2.SpacetimeBuilder()
#         response.polygon.latlngs = builder.polygon.latlngs
#         for timestamp in builder.stubs.keys():
#             image_object = builder.stubs[timestamp]
#             polygon_hash = hashlib.md5(str(polygon.to_latlngs()).encode()).hexdigest()
#             destination_stub = "user://{uuid}/{polygon_hash}_{timestamp}_{resource_name}.tif".format(
#                 uuid=uuid,
#                 polygon_hash=polygon_hash,
#                 timestamp=image_object.timestamp,
#                 resource_name=image_object.resource_name
#             )
#
#             try:
#                 filestubs = self._geotiff_transforms_handler.crop_image_object(image_object, polygon, projection, destination_stub)
#                 stub_urls = [user_api_utils.user_stub_to_signed_url(s) for s in filestubs]
#
#                 response.stubs[timestamp].download_urls.extend(stub_urls)
#                 response.stubs[timestamp].download_stubs.extend(filestubs)
#                 response.stubs[timestamp].timestamp = timestamp
#                 response.stubs[timestamp].resource_name = "crop_{polygon_hash}_{resource_name}".format(polygon_hash=polygon_hash, resource_name=image_object.resource_name)
#
#                 for k in builder.stubs[timestamp].metadata.keys():
#                     response.stubs[timestamp].metadata[k] = builder.stubs[timestamp].metadata[k]
#             except Exception:
#                 return api_utils.log_and_return_status("_crop_image_object failed on Image Object: {} {}".format(timestamp, image_object), 500, request, logger, exc_info=True)
#
#         return response
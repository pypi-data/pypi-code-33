import aether as ae
from aether.proto.api_pb2 import SpacetimeBuilder, BytesTransmission
from aether.dataobjects.Spacetime import Spacetime as SpacetimeDo
from aether.sky_utils import sky_utils
from flask import request
from aether_shared.utilities.user_api_utils import user_api_utils
from flask_restful import reqparse
import time, hashlib, tempfile
from google.protobuf import json_format
# from RestrictedPython import compile_restricted
# from RestrictedPython import safe_globals, utility_builtins
# import inspect
import base64

from aether_shared.utilities.firebase_utils import firebase_utils
from aether_shared.utilities.api_utils import api_utils
from api.base.PostMethodResourceBase import PostMethodResourceBase

import logging
logger = logging.getLogger(__name__)

class CloudGatewayResource(PostMethodResourceBase):
    """The CloudGateway handles interactions between Aether users via Sky() and cloud operations that download
    heavyweight data, like Spacetime() objects, rather than lightweight instructions or Firebase stored data.

    In other words, the CloudGateway downloads data from Google Storage, Google BigQuery, and other cloud resources
    that are not Firebase or lightweight instructions. The operations run by CloudGateway should be straightforward
    and linear, i.e., an instruction to download a Builder object (like SpacetimeBuilder) into its object (Spacetime).

    Transfers of data are always carried out by the use of ProtoBuffers.

    POST Download: Takes a *Builder protobuffer and creates a * object.
    """

    _pb_type_to_object = dict(
        # Spacetime=Spacetime(),
        SpacetimeBuilder=SpacetimeBuilder(),
    )

    _builder_to_object_map = dict(
        # SpacetimeBuilder=Spacetime(),
    )

    _post_methods = dict(
        DownloadStub="DownloadStub",
        DownloadSpacetime="DownloadSpacetime",
    )

    def __init__(self, global_objects):
        self._global_objects = global_objects
        super(CloudGatewayResource, self).__init__(global_objects, logger)

    def post(self):
        parser = reqparse.RequestParser(bundle_errors=True)
        parser.add_argument('uuid', type=str, required=True, location='json')
        parser.add_argument('method', type=str, required=True, location='json')
        args = parser.parse_args()

        if not self._global_objects.authenticator().is_authorized_user(uid=args["uuid"]):
            return api_utils.log_and_return_status(
                "Unauthorized UUID {}".format(args["uuid"]), 401, request, logger)

        if args["method"] not in self._post_methods:
            return api_utils.log_and_return_status(
                "Requested Method not supported:", 400, request, logger)

        try:
            func = getattr(self, self._post_methods[args["method"]])
        except AttributeError:
            return api_utils.log_and_return_status(
                "Requested Method not found on Resource:", 400, request, logger, exc_info=True)

        try:
            response, code = func(request)
            return api_utils.log_and_return_status(response, code, request, logger)
        except Exception:
            return api_utils.log_and_return_status("Method {} failed.".format(request), 500, request, logger, exc_info=True)

    def DownloadStub(self, request):
        """Retrieves a stub from the Google Storage bucket."""

        parser = reqparse.RequestParser(bundle_errors=True)
        parser.add_argument('download_stub', type=str, required=True, location='json')
        args = parser.parse_args()

        try:
            download_stub = args["download_stub"]
            filemanager = self._global_objects.filemanager()
            if not filemanager.stub_exists(download_stub):
                return api_utils.log_and_return_status("Failed to download blob. Blob does not exist: {}".format(download_stub), 500, request, logger, exc_info=True)
            else:
                temporary_file = filemanager.retrieve_stub(download_stub)
                b = BytesTransmission()
                b.contents = temporary_file.read()
                temporary_file.seek(0) # In case this file is cached; its read needs to be reset.
                return json_format.MessageToJson(b), 200
        except:
            return api_utils.log_and_return_status("An error occurred during downloading blob.".format(request), 500, request, logger, exc_info=True)

    # def UploadBlob(self, request):
    #     """
    #     Uploads a string object from the user Google Storage bucket.
    #     """
    #
    #     parser = reqparse.RequestParser(bundle_errors=True)
    #     parser.add_argument('uuid', type=str, required=True, location='json')
    #     parser.add_argument('doc_id', type=str, required=True, location='json')
    #     parser.add_argument('data', type=str, required=True, location='json')
    #     parser.add_argument('allow_overwrite', type=bool, required=False, default=False, location='json')
    #     args = parser.parse_args()
    #
    #     try:
    #         stub = "user://{uuid}/{doc_id}".format(uuid=args.uuid, doc_id=args.doc_id)
    #         filemanager = self._global_objects.filemanager()
    #         if filemanager.stub_exists(stub) and not args.allow_overwrite:
    #             return api_utils.log_and_return_status("Failed to upload blob. Blob already exists.".format(request), 500, request, logger, exc_info=True)
    #         else:
    #             tempfile = StringIO.StringIO()
    #             tempfile.write(args.data)
    #             filemanager.upload_stub(tempfile, stub)
    #             return user_api_utils.user_stub_to_signed_url(stub)
    #     except:
    #         return api_utils.log_and_return_status("An error occurred during uploading blob.".format(request), 500, request, logger, exc_info=True)
    #
    # def DownloadBlob(self, request):
    #     """
    #     Retrieves a string object from the user Google Storage bucket.
    #     """
    #
    #     parser = reqparse.RequestParser(bundle_errors=True)
    #     parser.add_argument('uuid', type=str, required=True, location='json')
    #     parser.add_argument('doc_id', type=str, required=True, location='json')
    #     args = parser.parse_args()
    #
    #     try:
    #         stub = "user://{uuid}/{doc_id}".format(uuid=args.uuid, doc_id=args.doc_id)
    #         filemanager = self._global_objects.filemanager()
    #         if not filemanager.stub_exists(stub):
    #             return api_utils.log_and_return_status("Failed to download blob. Blob does not exist.".format(request), 500, request, logger, exc_info=True)
    #         else:
    #             return filemanager.retrieve_stub(stub).read()
    #     except:
    #         return api_utils.log_and_return_status("An error occurred during downloading blob.".format(request), 500, request, logger, exc_info=True)


    def DownloadSpacetime(self, request):
        """
        Takes a *Builder object (like SpacetimeBuilder) as its "builder" key of the request and downloads the object
        (like Spacetime), and transfers that back to the user via a ProtocolBuffer.
        """

        parser = reqparse.RequestParser(bundle_errors=True)
        parser.add_argument('uuid', type=str, required=True, location='json')
        parser.add_argument('builder', type=str, required=True, location='json')
        parser.add_argument('url_only', type=bool, required=False, default=False, location='json')
        parser.add_argument('values_as_json', type=bool, required=False, default=False, location='json')
        args = parser.parse_args()

        builder = firebase_utils.verify_pb(args["builder"], SpacetimeBuilder(), return_pb_if_valid=True)
        if builder is None:
            return api_utils.log_and_return_status(
                "Request contains improperly formed builder object for builder_type.", 400, request, logger)

        # Download the requested SpacetimeBuilder using the (alpha) SpacetimeDynamic object. #Dogfood
        # TODO(astrorobotic): This should *absolutely not* be attributed to the UUID. It should be admin.
        uuid = args["uuid"]
        ae.GlobalConfig.set_user(uuid)
        with ae.SkySession() as sky:
            spacetime = SpacetimeDo.copy_builder_to_spacetime(builder, sky)

        # Run BuildtimeOperation if those have been added.
        if len(builder.btops) != 0:
            for op_i, op_string in enumerate(builder.btops):
                try:
                    op = self.deserialize_function(op_string.serialized_func)
                except Exception:
                    return api_utils.log_and_return_status(
                        "Request contains improperly formed BuildtimeOperation {} bytestring in builder.".format(op_i),
                        400, request, logger, exc_info=True)
                try:
                    spacetime = op(spacetime)
                except Exception:
                    return api_utils.log_and_return_status(
                        "BuildtimeOperation {} in builder failed during operation.".format(op_i),
                        422, request, logger, exc_info=True)

        # Now we complete the creation of the Spacetime object by converting to a Protobuffer.
        as_json = args["values_as_json"] if "values_as_json" in args else False
        built = spacetime.to_pb(serialize_as_json=as_json)

        # Instead of returning the array_values, upload the entire Spacetime protocol buffer to Google Cloud Storage,
        # then clear the array_values, and return the Spacetime protocol buffer with everything else, including the
        # link to the Google Cloud Storage.
        if "url_only" in args and args["url_only"]:
            built_hash = hashlib.md5(sky_utils.serialize_pb(built)).hexdigest()
            build_hash = hashlib.md5(sky_utils.serialize_pb(builder)).hexdigest()
            destination_stub = "user://{uuid}/{built_hash}_created_{timestamp}_from_{build_hash}.spacetime".format(
                uuid=args["uuid"],
                built_hash=built_hash,
                build_hash=build_hash,
                timestamp=time.time(),
            )
            built.download_stub = destination_stub
            built.download_url = user_api_utils.user_stub_to_signed_url(destination_stub)

            logger.info("Writing Spacetime {} to location {}".format(built_hash, destination_stub))
            with tempfile.NamedTemporaryFile(delete=True, mode="wb") as f:
                f.write(sky_utils.serialize_pb(built))
                self._global_objects.filemanager().upload_stub(f, destination_stub)
            built.array_values = None

        return json_format.MessageToJson(built), 200

    @staticmethod
    def deserialize_function(s):
        s = base64.urlsafe_b64decode(s)
        y = compile(s, "<inline>", "exec")
        loc = {}
        exec(y, None, loc)
        return loc[list(loc.keys())[0]]

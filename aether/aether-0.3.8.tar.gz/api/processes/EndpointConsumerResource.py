from flask import request
from flask_restful import Resource, reqparse
from aether_shared.utilities.api_utils import api_utils
import json
from flask_restful.utils import cors
from aether_shared.utilities.firebase_utils import firebase_utils
import aether_shared.sharedconfig as shared_cfg
from aether import AEPolygon, SkySession, GlobalConfig

import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class EndpointConsumerResource(Resource):

    def __init__(self, global_objects):
        self._global_objects = global_objects

    @cors.crossdomain(origin='*')
    def get(self, uuid, application_id):
        parser = reqparse.RequestParser(bundle_errors=True)
        parser.add_argument('polygon', type=str, required=True)
        # parser.add_argument('hostport', type=str, required=False, default=None, location='args')
        args = parser.parse_args()

        if not self._global_objects.authenticator().is_authorized_user(uid=uuid):
            return api_utils.log_and_return_status(
                "Unauthorized UUID {}".format(args["uuid"]), 401, request, logger)

        db = self._global_objects.firestore_client()

        app_ref = db.collection(shared_cfg._application_collection).document(application_id)
        compiled_app = firebase_utils.document_exists(app_ref, return_dict_if_exists=True)

        if compiled_app is None:
            return api_utils.log_and_return_status(
                "Requested Application ID does not exist.", 400, request, logger)

        try:
            polygon = AEPolygon().from_latlngs(args["polygon"])
        except Exception:
            return api_utils.log_and_return_status(
                "Request has incorrectly formed polygon.", 401, request, logger, exc_info=True)

        # hostport = self._ingress_hostport if args["hostport"] is None else args["hostport"]
        # logger.info("Using destination hostport: {}".format(hostport))

        try:
            GlobalConfig.set_user(compiled_app["owner_uuid"])
            client = SkySession().aether_client()
            uri_parameters = dict(polygon=polygon.to_latlngs(),
                                  payload=compiled_app["payload"])
            response = client.post_to("SkyApplicationManifest", {}, uri_parameters)
        except Exception:
            return api_utils.log_and_return_status("SkyApplication Application ID {} failed during operation.".format(application_id), 500, request, logger, exc_info=True)

        logger.info("Request {}. Response: {:.10000}".format(request, str(response)))
        return json.dumps(response)



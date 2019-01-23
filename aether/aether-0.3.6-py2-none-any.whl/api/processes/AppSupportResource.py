from aether.proto.api_pb2 import SkyApplication
from aether_shared.utilities.firebase_utils import firebase_utils
from aether_shared.utilities.api_utils import api_utils
from flask_restful import reqparse
from api.base.PostMethodResourceBase import PostMethodResourceBase
from aether.sky_utils import sky_utils
import aether_shared.sharedconfig as cfg

import time

# What to do about     response = json_format.MessageToJson(response) call after response.
# Fix pb.XXX values

import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class AppSupportResource(PostMethodResourceBase):
    """
    The AppSupportResource handles operations executed by the AppSupport() object.

    POST PublishApp: Saves/Publishes a SkyApplication for public usage.
    POST UpdateApp: Updated a SkyApplication already in public usage.
    """

    _post_methods = dict(
        PublishApp="PublishApp",
        UpdateApp="UpdateApp",
        GetAppInfo="GetAppInfo",
        GetUserApps="GetUserApps",
    )

    def __init__(self, global_objects):
        self._global_objects = global_objects
        super(AppSupportResource, self).__init__(global_objects, logger)

    def _getAppInfo(self, application_id):
        # Read App Info, if exists
        db = self._global_objects.firestore_client()
        app_ref = db.collection(cfg._application_collection).document(application_id)
        app_info = firebase_utils.document_exists(app_ref, return_dict_if_exists=True)
        return app_info

    def GetAppInfo(self, request):
        """
        The GetAppInfo retrieves all the information on the the published application_id.
        :param request:
        :return:
        """
        parser = reqparse.RequestParser(bundle_errors=True)
        parser.add_argument('uuid', type=str, required=True, location='json')
        parser.add_argument('application_id', type=str, required=True, location='json') # Required
        args = parser.parse_args()

        app_info = self._getAppInfo(args["application_id"])
        logging.info("Retrieved User {} Application {} Info {}; Request {}".format(
            args["uuid"], args["application_id"], app_info, request))

        return

    def GetUserApps(self, request):
        """
        The GetUserApps retrieves all the published Apps for the user, and the Apps' information.
        :param request:
        :return:
        """
        parser = reqparse.RequestParser(bundle_errors=True)
        parser.add_argument('uuid', type=str, required=True, location='json')
        args = parser.parse_args()

        apps = {}
        db = self._global_objects.firestore_client()
        app_refs = db.collection(cfg._application_collection).where(u'owner_uuid', u'==', unicode(args["uuid"])).get()
        for app_ref in app_refs:
            apps[app_ref.id] = app_ref.to_dict()

        logging.info("Retrieved User {} Applications {}; Request {}".format(args["uuid"], apps, request))
        return api_utils.log_and_return_status(apps, 200, request, logger)

    def UpdateApp(self, request):
        """
        The UpdateApp is identical to the PublishApp except that request is expected to contain an
        application_id parameter. The
        :param request:
        :return:
        """
        parser = reqparse.RequestParser(bundle_errors=True)
        parser.add_argument('uuid', type=str, required=True, location='json')
        parser.add_argument('payload', type=str, required=True, location='json')
        parser.add_argument('application_id', type=str, required=True, location='json') # Required
        args = parser.parse_args()

        return self.PublishApp(request, application_id=args["application_id"])

    def PublishApp(self, request, application_id=None):
        """
        :param request:
        :param application_id:
        :return:
        """
        parser = reqparse.RequestParser(bundle_errors=True)
        parser.add_argument('uuid', type=str, required=True, location='json')
        parser.add_argument('payload', type=str, required=True, location='json')
        if application_id is None:
            parser.add_argument('application_id', type=str, required=False, location='json')
        args = parser.parse_args()

        try:
            payload = sky_utils.deserialize_from_url(args["payload"])
        except:
            return api_utils.log_and_return_status(
                "Request contains improperly formed serialized SkyApplication.", 400, request, logger)

        sky_app = firebase_utils.verify_pb(payload, SkyApplication(), return_pb_if_valid=True)
        if sky_app is None:
            return api_utils.log_and_return_status(
                "Request contains improperly formed serialized SkyApplication.", 400, request, logger)

        db = self._global_objects.firestore_client()

        # Application Id?
        if application_id is None and args["application_id"] is None:
            doc_ref = db.collection(cfg._application_collection).document()
            application_id = doc_ref.id
        else:
            application_id = args["application_id"] if application_id is None else application_id
            doc_ref = db.collection(cfg._application_collection).document(application_id)

        dm = dict(
            owner_uuid=unicode(args["uuid"]),
            payload=args["payload"],
            input_structure=sky_app.input_structure,
            output_structure=sky_app.output_structure,
            application_name=sky_app.application_name,
            description=sky_app.description,
            submission_time=time.time(),
        )

        doc_ref.set(dm)

        logging.info("Published SkyApplication: Application {}; Request {}".format(sky_app, request))

        response = application_id
        return api_utils.log_and_return_status(response, 200, request, logger)

from flask import request
from flask_restful import reqparse
from aether_shared.utilities.firebase_utils import firebase_utils
from aether_shared.utilities.api_utils import api_utils
from aether_shared.utilities.services_util import services_util
from api.base.PostMethodResourceBase import PostMethodResourceBase
import aether_shared.sharedconfig as cfg
import time


import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# TODO(davidbernat): Split UserInfor into Public and Non-Public Objects


class UserAdminResource(PostMethodResourceBase):
    """
    The UserAdmin handles operates with users and their account data.

    POST CreateDevUser: Upgrades a user to user-developer.
    POST GetUserInformation: Returns the user info to self as dictionary.
    """

    _post_methods = dict(
        GetUserInformation="GetUserInformation",
        UpgradeUserToDeveloper="UpgradeUserToDeveloper",
    )

    def __init__(self, global_objects):
        self._global_objects = global_objects
        super(UserAdminResource, self).__init__(global_objects, logger)

    def post(self):
        parser = reqparse.RequestParser(bundle_errors=True)
        parser.add_argument('uuid', type=str, required=True, location='json')
        parser.add_argument('method', type=str, required=True, location='json')
        args = parser.parse_args()

        if not self._global_objects.authenticator().is_authorized_user(uid=args["uuid"]):
            return api_utils.log_and_return_status(
                "Unauthorized UUID {}".format(args["uuid"]), 401, request, logger)

        return services_util.run_method_on_handler(self, args["method"], self._post_methods, request, logger)

    def UpgradeUserToDeveloper(self, request):
        parser = reqparse.RequestParser(bundle_errors=True)
        parser.add_argument('uuid', type=str, required=True, location='json')
        parser.add_argument('is_power', default=False, type=bool, required=False, location='json')
        args = parser.parse_args()

        db = self._global_objects.firestore_client()
        user_ref = db.collection(cfg._user_quotas_collections).document(args["uuid"])

        if firebase_utils.document_exists(user_ref):
            return api_utils.log_and_return_status(
                "User {} is already a User-Developer.".format(args["uuid"]), 200, request, logger)

        if args["is_power"]:
            dm = dict(
                storage_quota_gb=10,
                storage_usage_gb=0,
                compute_quota_hr=5,
                compute_usage_hr=0,
                create_time=time.time(),
                user_type="PowerUserDeveloper",
            )
        else:
            dm = dict(
                storage_quota_gb=100,
                storage_usage_gb=0,
                compute_quota_hr=50,
                compute_usage_hr=0,
                create_time=time.time(),
                user_type="UserDeveloper",
            )

        user_ref.set(dm)

        return api_utils.log_and_return_status(
            "User {} created as a {}.".format(args["uuid"], dm["user_type"]), 200, request, logger)

    def GetUserInformation(self, request):
        parser = reqparse.RequestParser(bundle_errors=True)
        parser.add_argument('uuid', type=str, required=True, location='json')
        args = parser.parse_args()

        # Get the user record
        user_record = self._global_objects.authenticator().get_user(uid=args["uuid"])
        user_info = self._global_objects.authenticator().user_record_as_dict(user_record)

        # Add user-developer record if exists
        db = self._global_objects.firestore_client()
        user_ref = db.collection(cfg._user_quotas_collections).document(args["uuid"])

        user_dev_info = firebase_utils.document_exists(user_ref, return_dict_if_exists=True)
        if user_dev_info is not None:
            user_info.update(user_dev_info)

        logger.info("User {} Information {}; Request {}".format(args["uuid"], user_info, request))
        return api_utils.log_and_return_status(user_info, 200, request, logger)

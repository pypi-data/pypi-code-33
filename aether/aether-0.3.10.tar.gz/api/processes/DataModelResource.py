from aether_shared.utilities.services_util import services_util
from aether_shared.utilities.firebase_utils import firebase_utils
from aether_shared.utilities.api_utils import api_utils
from flask import request
from flask_restful import reqparse
from api.base.PostMethodResourceBase import PostMethodResourceBase
import aether_shared.sharedconfig as cfg

import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DataModelResource(PostMethodResourceBase):
    """
    The DataModelResource handles operations between users and their data model objects data.

    POST Save: Saves a DataModel DataObject.
    POST Load: Loads a DataModel DataObject.
    """

    _post_methods = dict(
        Save="Save",
        Load="Load",
    )

    def __init__(self, global_objects):
        self._global_objects = global_objects
        super(DataModelResource, self).__init__(global_objects, logger)

    def post(self):
        parser = reqparse.RequestParser(bundle_errors=True)
        parser.add_argument('uuid', type=str, required=True, location='json')
        parser.add_argument('method', type=str, required=True, location='json')
        args = parser.parse_args()

        if not self._global_objects.authenticator().is_authorized_user(uid=args["uuid"]):
            return api_utils.log_and_return_status(
                "Unauthorized UUID {}".format(args["uuid"]), 401, request, logger)

        return services_util.run_method_on_handler(self, args["method"], self._post_methods, request, logger)

    def Save(self, request):
        parser = reqparse.RequestParser(bundle_errors=True)
        parser.add_argument('uuid', type=str, required=True, location='json')
        parser.add_argument('data_object_type', type=str, required=True, location='json')
        parser.add_argument('data_object_id', type=str, required=False, location='json') # Not required.
        parser.add_argument('data_model', type=str, required=True, location='json')
        args = parser.parse_args()

        if args["data_object_type"] not in cfg._valid_data_model_types:
            return api_utils.log_and_return_status(
                "Request contains improperly formed data_model values", 400, request, logger)

        dm = firebase_utils.verify_json(args["data_model"], return_dict_if_valid=True)
        if dm is None:
            return api_utils.log_and_return_status(
                "Request contains improperly formed data_model values.", 400, request, logger)

        db = self._global_objects.firestore_client()
        user_ref = db.collection(cfg._user_datamodel_collection).document(args["uuid"])

        if "data_object_id" in args:
            doc_ref = user_ref.collection(args["data_object_type"]).document(args["data_object_id"])
            id = args["data_object_id"]
        else:
            doc_ref = user_ref.collection(args["data_object_type"]).document()
            id = doc_ref.id
        doc_ref.set(dm)

        return api_utils.log_and_return_status(dict(data_model_id=id), 200, request, logger)

    def Load(self, request):
        parser = reqparse.RequestParser(bundle_errors=True)
        parser.add_argument('uuid', type=str, required=True, location='json')
        parser.add_argument('data_object_type', type=str, required=True, location='json')
        parser.add_argument('data_object_id', type=str, required=True, location='json')
        args = parser.parse_args()

        if args["data_object_type"] not in cfg._valid_data_model_types:
            return api_utils.log_and_return_status(
                "Request contains improperly formed data_model values", 400, request, logger)

        db = self._global_objects.firestore_client()
        user_ref = db.collection(cfg._user_datamodel_collection).document(args["uuid"])

        doc_ref = user_ref.collection(args["data_object_type"]).document(args["data_object_id"])
        dm = firebase_utils.document_exists(doc_ref, return_dict_if_exists=True)

        if dm is None:
            return api_utils.log_and_return_status(
                "Requested Document ID does not exist.", 400, request, logger)

        return api_utils.log_and_return_status(dm, 200, request, logger)

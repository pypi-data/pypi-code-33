from aether_shared.utilities.services_util import services_util
from aether_shared.utilities.api_utils import api_utils
from flask import request
from flask_restful import Resource, reqparse

class PostMethodResourceBase(Resource):

    def __init__(self, global_objects, logger):
        self._global_objects = global_objects
        self._logger = logger

    def post(self):
        parser = reqparse.RequestParser(bundle_errors=True)
        parser.add_argument('uuid', type=str, required=True, location='json')
        parser.add_argument('method', type=str, required=True, location='json')
        args = parser.parse_args()

        if not self._global_objects.authenticator().is_authorized_user(uid=args["uuid"]):
            return api_utils.log_and_return_status(
                "Unauthorized UUID {}".format(args["uuid"]), 401, request, self._logger)

        return services_util.run_method_on_handler(self, args["method"], self._post_methods, request, self._logger)

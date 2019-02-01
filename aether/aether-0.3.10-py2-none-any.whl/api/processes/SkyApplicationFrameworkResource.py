from aether import SpacetimeBuilder
from aether_shared.utilities.firebase_utils import firebase_utils
from aether_shared.utilities.api_utils import api_utils
from flask_restful import reqparse
from flask import request
from flask_restful import Resource

import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

#####################################################################################################################
#
# An Application
#
#####################################################################################################################

import abc

class SkyFrameworkComponent(object):
    """An Application operates on an axis of turning SpacetimeBuilders into other SpacetimeBuilders.
        An Application contains the following components:

        1) An application which runs before it, originating from Search().
        2) A RequestParser containing the arguments required for processing at Post().
            a. 'uuid' (str) and 'builder' (str serialized SpacetimeBuilder pb) are included automatically (inherited), as
                well as validation steps for confirming the authorization of the user uuid and the correct parsing of the
                serialized SpacetimeBuilder pb into an object.
            b. No additional validation or processing at Post() (prior to entering function) are available.
        3) The RequestParser is called. The run() method of the application is called.
            a. The run method has the following parameters: run(request, args, uuid, builder)
            b. The run() method returns a SpacetimeBuilder pb and a Status json with the following fields:
                i. "code": an HTTP response code. 200 indicates success.
                ii. "message": a string message to communicate to the user regarding the performance of the system.
                iii. "ok": a boolean, indicating successful completion as intended
                iv: "reason": a string message indicating the reason if "ok" is False, ignored otherwise
        4) An application which runs after it.

            Add Method (e.g., train / infer).

    """

    @abc.abstractmethod
    def parseRequest(self, method_name):
        pass

    @abc.abstractmethod
    def availableMethods(self):
        pass

    # @abc.abstractmethod
    # def initialize(self):
    #     """Called once the first time the SkyApplication is called and persists indefinitely."""
    #     pass

    def __init__(self):
        pass



class SkyApplicationFrameworkResource(Resource):
    """An Application operates on an axis of turning SpacetimeBuilders into other SpacetimeBuilders.
    An Application contains the following components:

    1) An application which runs before it, originating from Search().
    2) A RequestParser containing the arguments required for processing at Post().
        a. 'uuid' (str) and 'builder' (str serialized SpacetimeBuilder pb) are included automatically (inherited), as
            well as validation steps for confirming the authorization of the user uuid and the correct parsing of the
            serialized SpacetimeBuilder pb into an object.
        b. No additional validation or processing at Post() (prior to entering function) are available.
    3) The RequestParser is called. The run() method of the application is called.
        a. The run method has the following parameters: run(request, args, uuid, builder)
        b. The run() method returns a SpacetimeBuilder pb and a Status json with the following fields:
            i. "code": an HTTP response code. 200 indicates success.
            ii. "message": a string message to communicate to the user regarding the performance of the system.
            iii. "ok": a boolean, indicating successful completion as intended
            iv: "reason": a string message indicating the reason if "ok" is False, ignored otherwise
    4) An application which runs after it.

        Add Method (e.g., train / infer).

    """

    def __init__(self, global_objects, sky_application):
        self._global_objects = global_objects
        self._sky_application = sky_application

    def post(self):
        parser = reqparse.RequestParser(bundle_errors=True)
        parser.add_argument('uuid', type=str, required=True, location='json')
        parser.add_argument('builders', type=str, required=True, action='append', location='json')
        parser.add_argument('method', type=str, required=True, location='json')
        args = parser.parse_args()

        uuid = args["uuid"]
        if not self._global_objects.authenticator().is_authorized_user(uid=uuid):
            return api_utils.log_and_return_status(
                "Unauthorized UUID {}".format(uuid), 401, request, logger)

        builders = []
        for builder in args.builders:
            builder = firebase_utils.verify_pb(builder, SpacetimeBuilder(), return_pb_if_valid=True)
            if builder is None:
                return api_utils.log_and_return_status(
                    "Request contains improperly formed builder object for builder_type.", 400, request, logger)
            builders.append(builder)

        try:
            method_args = self._sky_application.parseRequest()
        except Exception:
            return api_utils.log_and_return_status("SkyFrameworkComponent failed during argument parsing.", 400, request, logger, exc_info=True)

        if args.method not in self._sky_application.availableMethods():
            return api_utils.log_and_return_status(
                "Requested Method not supported: {}".format(request), 400, request, logger)

        try:
            func = getattr(self._sky_application, self._sky_application.availableMethods()[args.method])
        except AttributeError:
            return api_utils.log_and_return_status(
                "Requested Method not found on Resource:".format(request), 400, request, logger, exc_info=True)

        try:
            response, code = func(method_args, uuid, builders)
            return api_utils.log_and_return_status(response, code, request, logger)
        except Exception:
            return api_utils.log_and_return_status("SkyFrameworkComponent failed during operation.", 500, request, logger, exc_info=True)

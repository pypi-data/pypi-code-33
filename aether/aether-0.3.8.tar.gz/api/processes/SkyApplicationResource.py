from aether.proto.api_pb2 import SpacetimeBuilder, Spacetime, HttpResponse, SkyApplication, BoundMethod
from api.placeholder.SpacetimeMethodWrapper import SpacetimeMethodWrapper
from google.protobuf import json_format
from flask_restful import Resource, reqparse, request
from aether_shared.utilities.api_utils import api_utils
from aether_shared.utilities.firebase_utils import firebase_utils
from aether.app_io_utilities import app_io_utilities
from aether import AEPolygon, SkySession, GlobalConfig
import copy
import json
from aether.sky_utils import sky_utils


import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SkyApplicationResource(Resource):

    _structure_objects = dict(
        SpacetimeBuilder=SpacetimeBuilder(),
        Spacetime=Spacetime(),
        HttpResponse=HttpResponse(),
    )

    def __init__(self, global_objects):
        self._global_objects = global_objects

    def post(self):
        parser = reqparse.RequestParser(bundle_errors=True)
        parser.add_argument('uuid', type=str, required=True, location='json')
        parser.add_argument('payload', type=str, required=True, location='json')
        parser.add_argument('polygon', type=list, required=True, action="append", location='json')
        parser.add_argument('hostport', type=str, required=False, location='json')
        args = parser.parse_args()

        if not self._global_objects.authenticator().is_authorized_user(uid=args["uuid"]):
            return api_utils.log_and_return_status(
                "Unauthorized UUID {}".format(args["uuid"]), 401, request, logger)

        try:
            args["payload"] = sky_utils.deserialize_from_url(args["payload"])
        except:
            return api_utils.log_and_return_status(
                "Request contains improperly formed payload object.", 400, request, logger)

        application = firebase_utils.verify_pb(args["payload"], SkyApplication(), return_pb_if_valid=True)
        if application is None:
            return api_utils.log_and_return_status(
                "Request contains improperly formed payload object.", 400, request, logger)

        try:
            polygon = AEPolygon().from_latlngs(args["polygon"])
        except Exception:
            return api_utils.log_and_return_status(
                "Request contains improperly formed polygon object.", 400, request, logger)

        # hostport = self._ingress_hostport if args["hostport"] is None else args["hostport"]
        # logger.info("Using destination hostport: {}".format(hostport))

        try:
            response = self.run(polygon, application)
        except Exception:
            return api_utils.log_and_return_status("SkyApplication failed during operation.", 500, request, logger, exc_info=True)

        # This seems like the incorrect fix. Though this will work so long as output_structure takes only its current
        # value.
        # TODO(davidbernat): Potential Bug: Output_structure marshalling in SkyApplicationResource
        response = json.loads(response)

        logger.info("Request {}. Response: {:.10000}".format(request, str(response)))
        return response

    def run(self, polygon, sky_app):
        """

        # If the SkyApplication contains SkyMessage requests, we run those.
        # If the SkyApplication contains SkyApplication applications, we run those.
        # If the SkyApplication contains both, we throw an error.

        """

        object_buffer = {}

        # TODO(davidbernat): This use of a GlobalConfig is not threadsafe.
        GlobalConfig.set_user(sky_app.owner_uuid)
        client = SkySession().aether_client()
        for message_i, message in enumerate(sky_app.messages):

            # Message is either:
            # 1) a request object that receives the response from the previous message.
            # 2) a bound method to be applied to (a Spacetime) response

            if message.request_type == "MICROSERVICE":
                object_buffer = self._handle_microservice(client, object_buffer, polygon, message_i, message)

            if message.request_type == "BOUNDMETHOD":
                object_buffer = self._handle_boundmethod(object_buffer, message_i, message)

        string_output_structure = json.loads(sky_app.output_structure)
        output_structure = app_io_utilities.string_as_structure(string_output_structure, self._structure_objects)
        return self._marshal_return_value_from_buffer(object_buffer, output_structure)

    def _handle_boundmethod(self, object_buffer, message_i, message):
        try:
            # Sometimes json.loads returns unicode, sometimes strings. Need str, Protobufs act on strings!
            method = BoundMethod()
            method.ParseFromString(str(json.loads(message.request)))
            parameters = json.loads(method.parameters_as_json)

            string_output_structure = json.loads(message.output_structure)
            output_structure = app_io_utilities.string_as_structure(string_output_structure, self._structure_objects)
            if output_structure is None:
                msg = "Output Structure is not properly formed: " + str(string_output_structure)
                raise ValueError(msg)
        except Exception:
            raise ValueError("SkyApplication BoundMethod on Message {} could not be deserialized".format(message_i))

        try:
            func = getattr(SpacetimeMethodWrapper(object_buffer["Spacetime"]), method.method_name)
        except AttributeError:
            raise ValueError("SkyApplication BoundMethod on Message {} not found on Spacetime object".format(message_i))

        try:
            response = func(**parameters)
        except Exception:
            raise ValueError("SkyApplication BoundMethod on Message {} failed during operation".format(message_i))

        return self._marshal_output_to_buffer(object_buffer, response, output_structure)

    @staticmethod
    def _marshal_return_value_from_buffer(object_buffer, output_structure):
        if isinstance(output_structure, dict):
            response = {}
            for key, leaf in output_structure.iteritems():
                name = leaf.__class__.__name__
                response[key] = json_format.MessageToJson(object_buffer[name])
        else:
            name = output_structure.__class__.__name__
            response = json_format.MessageToJson(object_buffer[name])
        return response

    @staticmethod
    def _marshal_output_to_buffer(object_buffer, response, output_structure):
        # This updates the buffer with latest variable names using output_structure.
        if isinstance(output_structure, dict):
            for key, leaf in output_structure.iteritems():
                name = leaf.__class__.__name__
                object_buffer[name] = response[key]
        else:
            name = output_structure.__class__.__name__
            object_buffer[name] = response
        return object_buffer

    def _handle_microservice(self, client, object_buffer, polygon, message_i, message):
        try:
            request = json.loads(message.request)
            string_output_structure = json.loads(message.output_structure)
            output_structure = app_io_utilities.string_as_structure(string_output_structure, self._structure_objects)
            if output_structure is None:
                msg = "Output Structure is not properly formed: " + str(string_output_structure)
                raise ValueError(msg)
        except Exception:
            raise ValueError("SkyApplication Message {} had ill formed json.".format(message_i))

        # If the first message, we force the approximate of placeholder_input = dict(polygon=PlaceholderPolygon)
        # We replace the request["data"] with polygon.
        # Here we want placeholder_input = {"builder", "SpacetimeBuilder"}
        if message_i == 0:
            object_buffer["polygon"] = polygon.to_latlngs()
            request["data"]["polygon"] = polygon.to_latlngs()
        else:
            # Merge the builder with the current one. This is intended to preser new operations like btops.
            # TODO(davidbernat): This merge of Placeholders appears unstable with further development.
            try:
                message_builder = json_format.Parse(request["data"]["builder"], SpacetimeBuilder())
                buffer_builder = copy.deepcopy(object_buffer["SpacetimeBuilder"])
                buffer_builder.ClearField("btops")
                buffer_builder.btops.extend(message_builder.btops)
                request["data"]["builder"] = json_format.MessageToJson(buffer_builder)
            except Exception:
                raise ValueError("SkyApplication Message {} had ill formed SpacetimeBuilder.".format(message_i))

        response = client.post_request(request, output_structure)

        return self._marshal_output_to_buffer(object_buffer, response, output_structure)
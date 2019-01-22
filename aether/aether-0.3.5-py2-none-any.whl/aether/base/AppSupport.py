import json
import logging

import aether as ae
from aether.app_io_utilities import app_io_utilities
# from aether.base.placeholder.PlaceholderPolygon import PlaceholderPolygon
from aether.base.placeholder.PlaceholderSpacetime import PlaceholderSpacetime
from aether.proto.api_pb2 import PlaceholderSpacetimeBuilder
from aether.proto.api_pb2 import SkyMessage

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class AppSupport(object):
    """
    The AppSupport allows user-developers to write code to run locally or in the cloud with the same code.

    Nearly every function and operation on the Aether Platform is structured as a
    cloud-based microservice accessible by REST API (via the Aether client in python).
    This allows user-developers to easily transform Aether applications built and used
    in python into its own (sequence of) cloud-based microservice application accessible
    by REST API. This adds an important layer of portability, modularity, and reusability
    to the Aether applications, and aims to motivate user-developers to share applications
    and publish often to application users.

    The AppSupport object maintains this transformation and abstracts its functionality off
    the responsibility of the user-developer. In most cases, Aether applications built and
    used in python can be transformed into portable, shareable cloud applications by creating
    an AppSupport object and passing this through the application chain via the app argument.
    """

    def __init__(self):
        self._messages = []

    _placeholder_variants = dict(
        Polygon=ae.AEPolygon(None),
        SpacetimeBuilder=PlaceholderSpacetimeBuilder(),
        Spacetime=PlaceholderSpacetime(),
    )

    def add(self, request, input_structure, output_structure, request_type):
        message = SkyMessage()
        message.request = json.dumps(request)
        message.request_type = request_type
        # message.input_structure = json.dumps(app_io_utilities._structure_as_string(input_structure))
        message.output_structure = json.dumps(app_io_utilities._structure_as_string(output_structure))
        self._messages.append(message)

        response = app_io_utilities.mimic_placeholder_output_structure(
            output_structure, self._placeholder_variants, self)
        return response

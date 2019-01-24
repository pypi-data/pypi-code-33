from aether.proto.api_pb2 import BoundMethod, HttpResponse, Spacetime
from aether.proto.api_pb2 import PlaceholderSpacetime as PlaceholderSpacetime_pb
from aether.base.placeholder.Placeholder import Placeholder
import json

######################################################################
#
# This function helps set the is_placeholder attribute for the developer.
#
######################################################################

class PlaceholderSpacetime(Placeholder):

    def __init__(self):
        super(PlaceholderSpacetime, self).__init__()

    def initialize_pb(self):
        ps = PlaceholderSpacetime_pb()
        ps.is_placeholder_pb = True
        self._ps = ps

    def from_pb(self, pb):
        b = BoundMethod()
        b.method_name = "from_pb"
        parameters = dict()
        b.parameters_as_json = json.dumps(parameters)
        self._app.add(b.SerializeToString(), input_structure=None, output_structure=Spacetime(), request_type="BOUNDMETHOD")
        return pb

    def generate_image(self, ts, bands, transparent = True, show_now=True, save_to=None):
        b = BoundMethod()
        b.method_name = "generate_image"
        parameters = dict(bands=bands, ts=ts, transparent=transparent, show_now=show_now, save_to=save_to)
        b.parameters_as_json = json.dumps(parameters)
        self._app.add(b.SerializeToString(), input_structure=None, output_structure=HttpResponse(), request_type="BOUNDMETHOD")

    def generate_chart(self, bands, subsample_to=None):
        b = BoundMethod()
        b.method_name = "generate_chart"
        parameters = dict(bands=bands, subsample_to=subsample_to)
        b.parameters_as_json = json.dumps(parameters)
        self._app.add(b.SerializeToString(), input_structure=None, output_structure=HttpResponse(), request_type="BOUNDMETHOD")

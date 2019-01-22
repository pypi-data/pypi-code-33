from aether.proto.api_pb2 import PlaceholderPolygon as PlaceholderPolygon_pb
from aether.base.placeholder.Placeholder import Placeholder

######################################################################
#
# This function helps set the is_placeholder attribute for the developer.
#
######################################################################

class PlaceholderPolygon(Placeholder):

    def __init__(self):
        super(PlaceholderPolygon, self).__init__()

    def initialize_pb(self):
        ps = PlaceholderPolygon_pb()
        ps.is_placeholder_pb = True
        self._ps = ps

    def to_latlngs(self):
        return "{polygon_latlngs}"
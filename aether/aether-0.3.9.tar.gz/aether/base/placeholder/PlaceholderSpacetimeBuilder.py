from aether.proto.api_pb2 import PlaceholderSpacetimeBuilder as PlaceholderSpacetimeBuilder_pb
from aether.base.placeholder.Placeholder import Placeholder

######################################################################
#
# This function helps set the is_placeholder attribute for the developer.
#
######################################################################

class PlaceholderSpacetimeBuilder(Placeholder):

    def __init__(self):
        super(PlaceholderSpacetimeBuilder, self).__init__()

    def initialize_pb(self):
        ps = PlaceholderSpacetimeBuilder_pb()
        ps.is_placeholder_pb = True
        self._ps = ps

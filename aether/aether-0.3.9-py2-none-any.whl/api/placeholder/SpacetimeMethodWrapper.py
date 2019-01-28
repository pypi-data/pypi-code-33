import tempfile
from aether.dataobjects.Spacetime import Spacetime
from aether.proto.api_pb2 import HttpResponse
from aether.sky_utils import sky_utils

class SpacetimeMethodWrapper(object):

    def __init__(self, spacetime):
        """
        Spacetime variable may either be a protobuffer or a Spacetime object.
        Depending on which type the spacetime variable is, certain methods will be accessible and others will fail.
        """
        self._spacetime = spacetime

    def generate_image(self, ts, bands, transparent=True, show_now=True, save_to=None):
        filename = tempfile.NamedTemporaryFile(delete=True, suffix=".png")
        self._spacetime.generate_image(ts, bands, show_now=False, save_to=filename.name)
        with open(filename.name, "rb") as f:
            data = sky_utils.serialize_for_url(f.read())
            r = HttpResponse()
            r.data["image"] = data
            return r

    def generate_chart(self, bands, show_now=True, save_to=None, subsample_to=None):
        filename = tempfile.NamedTemporaryFile(delete=True, suffix=".png")
        self._spacetime.generate_chart(bands, show_now=False, save_to=filename.name, subsample_to=subsample_to)
        with open(filename, "rb") as f:
            data = sky_utils.serialize_for_url(f.read())
            r = HttpResponse()
            r.data["image"] = data
            return r

    def from_pb(self):
        return Spacetime.from_pb(self._spacetime)


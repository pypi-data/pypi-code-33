name = "aether"
__version__ = "0.3.4"

print("Welcome to Aether Platform.")

import aetheruserconfig as cfg
from aether.Sky import Sky as SkyEngine

# User objects
from aether.dataobjects.AEFeatureCollection import AEFeatureCollection
from aether.dataobjects.AEPolygon import AEPolygon
from aether.dataobjects.Spacetime import Spacetime

# Sky request/response objects
from aether.session.GlobalConfig import GlobalConfig as _GlobalConfig
from aether.session.SkySession import SkySession
from aether.proto.api_pb2 import SpacetimeBuilder, HttpResponse
from aether.proto.api_pb2 import PlaceholderSpacetimeBuilder

# Objects Services Depend On
from aether.base.QueryParameter import QueryParameter

# User Services
from aether.base.AppSupport import AppSupport

# Sky request/response Placeholder objects
# from aether.base.placeholder.PlaceholderPolygon import PlaceholderPolygon


import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


##########################################
#
# For accessing the GlobalConfig directly
# from its Singleton
#
############################################

GlobalConfig = _GlobalConfig._getInstance()

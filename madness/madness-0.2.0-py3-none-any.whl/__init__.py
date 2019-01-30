#!/usr/bin/env python3.7

from dataclasses import dataclass

from werkzeug.wrappers import Response as response
from werkzeug.utils import redirect

from .aws import LambdaMixIn
from .cors import CORSMixIn
from .restful import RESTFulRoutesMixIn
from .application import ApplicationMixIn
from .context import request, context

__all__ = ()

@dataclass
class Madness(CORSMixIn, LambdaMixIn, RESTFulRoutesMixIn, ApplicationMixIn):
    """
    """

from ..models import *

from meapp.api.authentications import ExpiredTokenAuthentication



class AdminTokenAuth(ExpiredTokenAuthentication):
    model = AdminToken
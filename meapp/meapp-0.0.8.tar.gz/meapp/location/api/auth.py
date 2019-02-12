from ..models import *

try:
    from eeapp.jsonapi import ExpiredTokenAuthentication
except:
    from jsonapi.authentications import ExpiredTokenAuthentication



class AdminTokenAuth(ExpiredTokenAuthentication):
    pass
    model = AdminToken
from .models import RawCid
from rest_framework import authentication
import logging


class CIDAuthentication(authentication.BaseAuthentication):
    def authenticate(self, request):
        if len(request.data) == 0 or request.data[0].get('cid', None) is None:
            return None
        return (None, None)

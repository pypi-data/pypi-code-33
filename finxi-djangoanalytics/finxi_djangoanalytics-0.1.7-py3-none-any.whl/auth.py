from .models import Cid
from rest_framework import authentication
import logging


class CIDAuthentication(authentication.BaseAuthentication):
    def authenticate(self, request):
        if len(request.data) == 0 or request.data[0].get('cid', None) is None:
            return None
        hit_dict = request.data[0]
        trackable = Cid.objects.auth(hit_dict, 'cid') 
        return (trackable, None)

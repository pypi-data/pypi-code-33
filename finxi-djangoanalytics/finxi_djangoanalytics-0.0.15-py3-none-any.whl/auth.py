from .models import User
from rest_framework import authentication
from .models import RawHit


class CIDAuthentication(authentication.BaseAuthentication):
    def authenticate(self, request):
        if len(request.data) == 0 or request.data[0].get('cid', None) is None:
            return None
        user = User.objects.auth_user(request.data[0])
        return (user, None)

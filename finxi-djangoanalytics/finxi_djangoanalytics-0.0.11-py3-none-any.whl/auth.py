from .models import User
from rest_framework import authentication
from .models import RawHit


class CIDAuthentication(authentication.BaseAuthentication):
    def authenticate(self, request):
        if len(request.data) == 0 or request.data[0].get('cid', None) is None:
            return None
        try:
            cid = request.data[0]['cid']
            user = User.objects.get(cid=cid)
        except User.DoesNotExist:
            user = User(cid=cid,
                        first_session_source=request.data[0].get('cs', ''),
                        first_session_medium=request.data[0].get('cm', ''),
                        first_campaign_name=request.data[0].get('cn', ''),
                        first_campaign_keyword=request.data[0].get('ck', ''))
            user.save()
        if request.data[0].get('uid', None) is not None and user.user_id == '':
            user.user_id = request.data[0].get('uid', None)
            user.attribution_path = RawHit.objects.attribution_path(user)
            user.save()
        return (user, None)

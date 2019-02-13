from rest_framework import authentication
from rest_framework import exceptions
from datetime import datetime,timedelta
import pytz

from rest_framework.exceptions import APIException


from rest_framework import exceptions
# from rest_framework.authentication import TokenAuthentication
from rest_framework import HTTP_HEADER_ENCODING, exceptions
# from rest_framework.authtoken.models import Token
from django.utils.translation import ugettext_lazy as _



class TokenAuthentication(authentication.BaseAuthentication):

    model = None
    """
    A custom token model may be used, but must have the following properties.

    * key -- The string identifying the token
    * user -- The user to which the token belongs
    """

    def authenticate(self, request):

        auth = get_authorization_header(request).split()
        if auth:
            token = auth[0]
            return self.authenticate_credentials(token)
        raise APIException(detail='loss token')



    def authenticate_credentials(self, key):
        try:
            key = str(key, 'utf-8')
            token = self.model.objects.select_related('user').get(key=key)
        except self.model.DoesNotExist:
            raise exceptions.AuthenticationFailed(_('Invalid token.'))

        if not token.user.is_active:
            raise exceptions.AuthenticationFailed(_('User inactive or deleted.'))

        return (token.user, token)

    def authenticate_header(self, request):
        return 'Token'

class ExpiredTokenAuthentication(authentication.BaseAuthentication):

    model = None
    """
    A custom token model may be used, but must have the following properties.

    * key -- The string identifying the token
    * user -- The user to which the token belongs
    """

    def authenticate(self, request):

        auth = get_authorization_header(request).split()
        if auth:
            token = auth[0]
            return self.authenticate_credentials(token)
        raise APIException(detail='loss token')



    def authenticate_credentials(self, key):
        try:
            key = str(key, 'utf-8')
            print("====dd",key)
            token = self.model.objects.select_related('user').get(key=key)
        except self.model.DoesNotExist:
            raise exceptions.AuthenticationFailed(_('Invalid token.'))

        if not token.user.is_active:
            raise exceptions.AuthenticationFailed(_('User inactive or deleted.'))

        # if self.userModel is not None:
        #     ecs = ['token','user',self.userModel]
        #     u = eval('.'.join(ecs))
        #     return (u,token)

        return (token.user, token)

    def authenticate_header(self, request):
        return 'Token'







#
#
# class SellerTokenAuthentication(authentication.BaseAuthentication):
#     def authenticate(self, request):
#         method = request.method
#         token = ''
#         # print request.POST
#         # print request.GET
#         # print request.data
#
#         if method == 'POST':
#
#             try:
#                 token = request.POST['token']
#             except:
#                 raise exceptions.AuthenticationFailed('need token')
#
#         if method == 'GET':
#             try:
#                 token = request.GET['token']
#             except:
#                 raise exceptions.AuthenticationFailed('need token')
#
#
#         if not token:
#             return None
#         try:
#             tokenObj = authentication.Token.objects.get(key=token)
#             user = tokenObj.user
#         except authentication.Token.DoesNotExist:
#             print('have not '+token)
#             raise exceptions.AuthenticationFailed('No such user')
#         return (user, None)




def get_authorization_header(request):
    """
    Return request's 'Authorization:' header, as a bytestring.

    Hide some test client ickyness where the header can be unicode.
    """
    auth = request.META.get('HTTP_TOKEN', b'')

    if isinstance(auth, type('')):
        # Work around django test client oddness
        auth = auth.encode(HTTP_HEADER_ENCODING)
    return auth
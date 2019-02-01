from rest_framework import permissions

from two_factor_auth.models import Totp
from two_factor_auth.views.utils import user_has_totp
from two_factor_auth.strings import TWO_FACTOR_AUTH_REQUIRED, INVALID_MFA_CODE_ERROR

from rest_framework import status
from rest_framework.exceptions import APIException


class TwoFactorAuthRequired(APIException):
    status_code = status.HTTP_403_FORBIDDEN
    default_detail = TWO_FACTOR_AUTH_REQUIRED

class InvalidToken(APIException):
    status_code = status.HTTP_403_FORBIDDEN
    default_detail = INVALID_MFA_CODE_ERROR

class HasTOTPEnabled(permissions.BasePermission):
    def has_permission(self, request, view):
        if user_has_totp(request.user):
            return True
        else:
            raise TwoFactorAuthRequired

class TOTPTokenRequiredOnDeletePostPutPatch(permissions.BasePermission):
    def has_permission(self, request, view):
        if not user_has_totp(request.user):
            return True
        else:
            if request._request.method in ['DELETE', 'POST', 'PUT', 'PATCH']:
                token = request.GET.get('token', None)
                if token:
                    totp = Totp.objects.get(user=request.user)
                    if totp.verify_token(token):
                        return True
                    else:
                        raise InvalidToken
                else:
                    raise TwoFactorAuthRequired
            else:
                return True
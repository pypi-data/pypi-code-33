from rest_framework import generics, views, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from django.conf import settings

from two_factor_auth.models import Totp
from two_factor_auth.serializers import TwoFactorAuthSerializer, TwoFactorAuthEnableSerializer, TwoFactorAuthBackupCodeSerializer, \
    VerifyTokenSerializer
from two_factor_auth.permissions import TOTPTokenRequiredOnDeletePostPutPatch


class TwoFactorAuthMixin(object):
    """
    Mixin that defines queries for Totp objects.
    """

    def get_object(self):
        """Gets the current user's Totp instance"""
        instance, created = Totp.objects.get_or_create(user=self.request.user)
        return instance


class TwoFactorAuthDetail(TwoFactorAuthMixin, generics.RetrieveDestroyAPIView):
    """
    class::TwoFactorAuthDetail()

    View for requesting data about TwoFactorAuth and deleting Totp.
    """
    if getattr(settings, "TOKEN_REQUIRED_ON_DISABLE_AND_BACKUP_RECOVERY", True):
        permission_classes = (IsAuthenticated, TOTPTokenRequiredOnDeletePostPutPatch)
    else:
        permission_classes = (IsAuthenticated,)
    serializer_class = TwoFactorAuthSerializer

    def perform_destroy(self, instance):
        """
        The delete method should disable Totp for this user.

        :raises rest_framework.exceptions.ValidationError: If MFA is not
            enabled.
        """
        instance.enabled = False
        instance.save()


class TwoFactorAuthEnableView(TwoFactorAuthMixin, generics.UpdateAPIView):
    permission_classes = (IsAuthenticated,)
    serializer_class = TwoFactorAuthEnableSerializer


class TwoFactorBackupCodeDetail(TwoFactorAuthMixin, generics.UpdateAPIView):
    if getattr(settings, "TOKEN_REQUIRED_ON_DISABLE_AND_BACKUP_RECOVERY", True):
        permission_classes = (IsAuthenticated, TOTPTokenRequiredOnDeletePostPutPatch)
    else:
        permission_classes = (IsAuthenticated,)
    serializer_class = TwoFactorAuthBackupCodeSerializer


class TwoFactorVerifyToken(views.APIView, TwoFactorAuthMixin):
    permission_classes = (IsAuthenticated,)

    def post(self, request, *args, **kwargs):
        totp = self.get_object()
        serializer = VerifyTokenSerializer(data=self.request.data)

        if serializer.is_valid():
            token = serializer.validated_data['token']
            verified = totp.verify_token(token)

            return Response(data={"verified": verified}, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
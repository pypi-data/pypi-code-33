from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist
from django.http import Http404
from django.urls import reverse
from django.views.generic.base import TemplateView
from rest_framework import status
from rest_framework.parsers import JSONParser
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from staff.conf import settings
from staff.models import Profile
from staff.serializers import EditableProfileSerializer, UserSerializer
from staff.utils.auth import TokenAuthentication, secure


@secure
class EditProfile(TemplateView):
    template_name = "staff/edit.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        try:
            user = User.objects.get(pk=self.request.user.pk)
        except User.DoesNotExit:
            raise Http404
        context["user"] = user
        serializer = UserSerializer(user)
        context["serialized_user"] = serializer.data
        context["api"] = {
            "sync": reverse("staff-sync-profile"),
            "patch": reverse("staff-patch-profile"),
            "token": settings.SECRET_TOKEN,
        }
        return context


class PatchProfile(APIView):
    """
    Patch a profile
    """

    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)
    parser_classes = (JSONParser,)

    def patch(self, request, format=None):
        profile_id = request.data.get("id", None)
        try:
            profile = Profile.objects.get(pk=profile_id)
        except ObjectDoesNotExist:
            return Response(
                {"msg": "Profile not found"}, status=status.HTTP_404_NOT_FOUND
            )
        serializer = EditableProfileSerializer(
            profile, data=request.data, partial=True
        )
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

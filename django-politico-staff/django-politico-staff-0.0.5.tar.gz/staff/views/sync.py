from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist
from rest_framework import status
from rest_framework.parsers import JSONParser
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from staff.celery import sync_slack_users
from staff.utils.auth import TokenAuthentication


class SyncUser(APIView):
    """
    Request a users profile synced from Slack.
    """

    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)
    parser_classes = (JSONParser,)

    def post(self, request, format=None):
        pk = request.data.get("user", None)
        try:
            user = User.objects.get(pk=pk)
        except ObjectDoesNotExist:
            return Response(
                {"msg": "User not found"}, status=status.HTTP_404_NOT_FOUND
            )
        sync_slack_users.delay([user.pk])
        return Response({"msg": "Requested sync with Slack"})

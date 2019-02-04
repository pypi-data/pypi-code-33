from django.contrib.auth.models import User
from rest_framework.viewsets import ReadOnlyModelViewSet

from staff.conf import settings
from staff.serializers import UserSerializer


class StafferViewSet(ReadOnlyModelViewSet):
    serializer_class = UserSerializer
    authentication_classes = (settings.API_AUTHENTICATION_CLASS,)
    permission_classes = (settings.API_PERMISSION_CLASS,)
    pagination_class = None

    def get_queryset(self):
        queryset = User.objects.filter(is_staff=True)
        is_active = self.request.query_params.get("active", None) in [
            "true",
            "1",
        ]
        if is_active:
            queryset = queryset.filter(is_active=True)
        return queryset

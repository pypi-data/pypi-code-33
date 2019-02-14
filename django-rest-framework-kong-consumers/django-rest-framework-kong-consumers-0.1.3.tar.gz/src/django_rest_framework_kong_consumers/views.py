from django.contrib.auth.models import Group
from rest_framework import viewsets

from .serializers import ConsumerSerializer, GroupSerializer
from .models import Consumer


class ConsumerViewSet(viewsets.ReadOnlyModelViewSet):

    serializer_class = ConsumerSerializer
    lookup_field = 'kong_consumer_id'

    def get_queryset(self):
        user = self.request.user
        if user.is_anonymous:
            return Consumer.objects.none()
        elif user.is_staff:
            return Consumer.objects.all()
        else:
            return Consumer.objects.filter(pk=self.request.user.pk)

class GroupViewSet(viewsets.ReadOnlyModelViewSet):

    serializer_class = GroupSerializer
    lookup_field = 'id'

    def get_queryset(self):
        return Group.objects.all()

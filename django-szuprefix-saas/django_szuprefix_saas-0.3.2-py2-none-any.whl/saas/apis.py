# -*- coding:utf-8 -*-
from django_szuprefix.api.permissions import DjangoModelPermissionsWithView

from .apps import Config

from . import models, mixins, serializers, permissions

from rest_framework import viewsets, decorators, response
from django_szuprefix.api import mixins as api_mixins
from django_szuprefix.api.helper import register

__author__ = 'denishuang'


class PartyViewSet(viewsets.ModelViewSet):
    queryset = models.Party.objects.all()
    serializer_class = serializers.PartySerializer
    permission_classes = [permissions.IsAdminUser]


register(Config.label, 'party', PartyViewSet)


class WorkerViewSet(api_mixins.BatchCreateModelMixin, mixins.PartyMixin, viewsets.ModelViewSet):
    queryset = models.Worker.objects.all()
    serializer_class = serializers.WorkerSerializer
    filter_fields = {
        'number': ['exact', 'in']
    }
    
    def get_serializer_class(self):
        if self.action == 'list':
            return serializers.WorkerListSerializer
        return super(WorkerViewSet, self).get_serializer_class()


    # permission_classes = mixins.PartyMixin.permission_classes + [DjangoModelPermissionsWithView]

    @decorators.list_route(['get'], permission_classes=[permissions.IsSaasWorker])
    def current(self, request):
        serializer = serializers.CurrentWorkerSerializer(self.worker, context={'request': request})
        return response.Response(serializer.data)


    @decorators.list_route(['post'], permission_classes=[permissions.IsSaasWorker])
    def update_or_create(self, request):
        serializer = self.get_serializer() #serializers.WorkerSerializer(self.worker, context={'request': request})
        return response.Response(serializer.data)

register(Config.label, 'worker', WorkerViewSet)

from . import models
from . import serializers
from rest_framework import viewsets, permissions


class ComputationalToolViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for the ComputationalTool class"""

    queryset = models.ComputationalTool.objects.all()
    serializer_class = serializers.ComputationalToolSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        name = self.request.query_params.get('name', None)

        if name:
            return self.queryset.filter(name=name)

        return self.queryset


class ComputationalWFViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for the ComputationalWF class"""

    queryset = models.ComputationalWF.objects.all()
    serializer_class = serializers.ComputationalWFSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        name = self.request.query_params.get('name', None)

        if name:
            return self.queryset.filter(name=name)

        return self.queryset

from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.decorators import list_route
from django_pivot.contrib import rest_framework


class MeteoViewSet(rest_framework.PivotViewSetMixin, viewsets.ViewSet):
    @list_route(
        renderer_classes=rest_framework.RENDERERS,
    )
    def pivot(self, request, format=None):
        return self._export_pivot(request)

from . import models
from . import serializers
from rest_framework import viewsets, permissions


class RegionViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for the Region class"""

    queryset = models.Region.objects.all()
    serializer_class = serializers.RegionSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        name = self.request.query_params.get('name', None)

        if name:
            return self.queryset.filter(name=name)

        return self.queryset


class CpGViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for the IlluminaMethylation450 class"""

    queryset = models.CpG.objects.all()
    serializer_class = serializers.IlluminaMethylation450Serializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        name = self.request.query_params.get('name', None)
        chr = self.request.query_params.get('chr', None)
        mapinfo = self.request.query_params.get('mapinfo', None)

        if name:
            return self.queryset.filter(name=name)

        if chr and mapinfo:
            return self.queryset.filter(chr=chr, mapinfo=mapinfo)

        return self.queryset


class CpGHasTranscriptRegionsViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for the CpGHasTranscriptRegions class"""

    queryset = models.CpGHasTranscriptRegions.objects.all()
    serializer_class = serializers.CpGHasTranscriptRegionsSerializer
    permission_classes = [permissions.IsAuthenticated]

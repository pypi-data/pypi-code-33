# -*- coding: utf-8 -*-
from collections import OrderedDict
import requests

from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import APIException
from rest_framework.filters import SearchFilter
from rest_framework.response import Response
from rest_framework.status import HTTP_200_OK

from . import filters, models, serializers, services


class ArticleViewSet(viewsets.ModelViewSet):
    """ViewSet for viewing and editing Articles."""

    queryset = models.Article.objects.fast()
    serializer_class = serializers.ArticleSerializer
    filter_backends = (DjangoFilterBackend, SearchFilter)
    filterset_class = filters.ArticleFilter
    search_fields = ('description', )

    @action(detail=True, methods=['get'], url_path='eutils')
    def eutils(self, request, pk=None):
        instance = self.get_object()
        efetch = requests.get(instance.fetch_url)
        esummary = requests.get(instance.summary_url)

        if efetch.status_code != 200:
            raise APIException(
                detail='Could not fetch from eutils',
                code=efetch.status_code,
            )

        if esummary.status_code != 200:
            raise APIException(
                detail='Could not fetch from eutils',
                code=esummary.status_code,
            )

        data = services.parse_efetch(
            efetch.text,
            esummary.json(),
            instance.identifier
        )

        return Response(OrderedDict(data), HTTP_200_OK)

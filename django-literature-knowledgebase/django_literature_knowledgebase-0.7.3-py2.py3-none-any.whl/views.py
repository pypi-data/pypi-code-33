# -*- coding: utf-8 -*-
from collections import OrderedDict
import requests

from rest_framework.exceptions import APIException
from rest_framework.parsers import JSONParser
from rest_framework.response import Response
from rest_framework.status import HTTP_200_OK
from rest_framework.views import APIView

from . import services, utils


class PubmedArticleView(APIView):

    parser_classes = (JSONParser, )

    def get(self, request, pubmed_id, **kwargs):
        efetch = requests.get(utils.build_efetch_url(pubmed_id))
        esummary = requests.get(utils.build_esummary_url(pubmed_id))

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
            pubmed_id,
        )

        return Response(OrderedDict(data), HTTP_200_OK)

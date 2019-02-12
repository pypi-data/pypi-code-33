import logging
import urllib.request as http
import urllib.parse as parser
from rest_framework import status
from .auth import CIDAuthentication
from .process import Analytics
from rest_framework.views import APIView
from rest_framework.response import Response
from .parser import AnalyticsHitParser
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from rest_framework.permissions import IsAuthenticated


post_url = 'https://www.google-analytics.com/batch' 
handler = None


class AnalyticsProcessor(APIView):
    authentication_classes = (CIDAuthentication,)
    permission_classes = ()
    parser_classes = (AnalyticsHitParser,)

    def post(self, request, format=None):
        try:
            hit_dicts = request.data
            analytics = Analytics(request.user.id)
            if handler is None:
                [analytics.default(hit_dict) for hit_dict in hit_dicts]
            else:
                [handler(hit_dict, request.user.id)
                 for hit_dict in hit_dicts]
            return Response(status=status.HTTP_200_OK)
        except Exception:
            logging.exception("message")
        return Response(status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def send_to_ga(self, request):
        hits = [parser.urlencode(hit_dict) for hit_dict in request.data]
        hits_string = '\n'.join(hits).encode('ascii')
        http.urlopen(http.Request(post_url, hits_string))

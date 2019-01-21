import logging
import urllib.request as http
import urllib.parse as parser
from .models import Hit
from rest_framework import status
from .auth import CIDAuthentication
from .parser import AnalyticsHitParser
from rest_framework.views import APIView
from rest_framework.response import Response
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
            process_functions = [self.user_hit_function(request.user, hit_dict)
                                 for hit_dict in hit_dicts]
            if handler is None:
                [process() for process in process_functions]
            else:
                [handler(process_function) 
                 for process_function in process_functions]
            return Response(status=status.HTTP_200_OK)
        except Exception:
            logging.exception("message")
        return Response(status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def user_hit_function(self, user, hit_dict):
        def user_hit():
            return self.process(user, hit_dict)
        return user_hit

    def process(self, user, hit_dict):
        user.update_custom_variables(hit_dict)
        hit = Hit.objects.create(hit_dict, user)
        user.update_last_hit(hit)
        return user, hit

    def send_to_ga(self, request):
        hits = [parser.urlencode(hit_dict) for hit_dict in request.data]
        hits_string = '\n'.join(hits).encode('ascii')
        http.urlopen(http.Request(post_url, hits_string))

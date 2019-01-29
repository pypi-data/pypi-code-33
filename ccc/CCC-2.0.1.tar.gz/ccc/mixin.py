from oauth2_provider.contrib.rest_framework import OAuth2Authentication
from rest_framework.authentication import (BasicAuthentication,
                                           SessionAuthentication)
from rest_framework.pagination import PageNumberPagination
from rest_framework.parsers import FormParser, JSONParser, MultiPartParser
from rest_framework.permissions import IsAuthenticated


class LargeResultsSetPagination(PageNumberPagination):
    page_size = 1000
    page_size_query_param = 'page_size'
    max_page_size = 10000


class StandardResultsSetPagination(PageNumberPagination):
    page_size = 100
    page_size_query_param = 'page_size'
    max_page_size = 1000


class AuthMixin(object):
    authentication_classes = (OAuth2Authentication, SessionAuthentication, BasicAuthentication)
    permission_classes = (IsAuthenticated,)


class ParsersMixin(object):
    parser_classes = [JSONParser, FormParser, MultiPartParser]


class AuthParsersMixin(AuthMixin, ParsersMixin):
    pagination_class = StandardResultsSetPagination

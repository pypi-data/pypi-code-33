from django.views.decorators.csrf import ensure_csrf_cookie
from django.views.generic import UpdateView
from rest_framework import permissions
from rest_framework.response import Response
from rest_framework.utils import json
from rest_framework.views import APIView

from jsql.connector import JSQLConnector
from jsql.executor import JSQLExecutor


class SelectView(APIView):
    permission_classes = (permissions.AllowAny,)

    @classmethod
    def get_extra_actions(cls):
        return []

    def post(self, request, format=None):
        ex = JSQLExecutor()
        return Response(ex.executeSelect(request))


class InsertView(APIView):
    permission_classes = (permissions.AllowAny,)

    @classmethod
    def get_extra_actions(cls):
        return []

    def post(self, request, format=None):
        ex = JSQLExecutor()
        return Response(ex.executeInsert(request))


class UpdateView(APIView):
    permission_classes = (permissions.AllowAny,)

    @classmethod
    def get_extra_actions(cls):
        return []

    def post(self, request, format=None):
        ex = JSQLExecutor()
        return Response(ex.executeUpdateAndDelete(request))


class DeleteView(APIView):
    permission_classes = (permissions.AllowAny,)

    @classmethod
    def get_extra_actions(cls):
        return []

    def post(self, request, format=None):
        ex = JSQLExecutor()
        return Response(ex.executeUpdateAndDelete(request))

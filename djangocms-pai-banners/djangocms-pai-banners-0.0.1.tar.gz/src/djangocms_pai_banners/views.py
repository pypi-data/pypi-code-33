from django.shortcuts import render
from django.views.generic.edit import View
from django.contrib import messages
from django.shortcuts import redirect
from django.core.validators import validate_email
from django import forms
from django.utils.translation import ugettext_lazy as _
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework import viewsets

from .models import Banner
from .serializers import BannerSerializer


class BannerViewSet(viewsets.ReadOnlyModelViewSet):
    """
    A simple ViewSet for viewing Banners.
    """
    queryset = Banner.objects.all()
    serializer_class = BannerSerializer

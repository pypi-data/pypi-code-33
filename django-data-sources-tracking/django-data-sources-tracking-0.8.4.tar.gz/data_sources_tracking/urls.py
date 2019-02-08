# -*- coding: utf-8 -*-
from rest_framework import routers

from . import viewsets

app_name = 'data_sources_tracking'
router = routers.SimpleRouter()
router.register(r'', viewsets.FileViewSet)

default_router = routers.DefaultRouter()
default_router.register(r'files', viewsets.FileViewSet)


urlpatterns = default_router.urls

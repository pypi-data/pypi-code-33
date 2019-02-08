# -*- coding: utf-8 -*-
from django.conf.urls import url

from rest_framework import routers

from . import views, viewsets


app_name = 'literature_knowledgebase'
router = routers.SimpleRouter()
router.register(r'', viewsets.ArticleViewSet)

default_router = routers.DefaultRouter()
default_router.register(r'articles', viewsets.ArticleViewSet)


urlpatterns = default_router.urls

urlpatterns += [
    url(
        r'^pubmed-articles/(?P<pubmed_id>[0-9]+)/$',
        views.PubmedArticleView.as_view(),
        name='pubmed-articles-detail',
    ),
]

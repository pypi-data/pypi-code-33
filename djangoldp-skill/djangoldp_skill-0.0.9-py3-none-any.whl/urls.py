"""djangoldp skill URL Configuration"""
from django.conf.urls import url

from djangoldp.permissions import AnonymousReadOnly
from djangoldp.views import LDPViewSet
from .models import Skill

urlpatterns = [
    url(r'^skills/', LDPViewSet.urls(model=Skill, permission_classes=[AnonymousReadOnly])),
]

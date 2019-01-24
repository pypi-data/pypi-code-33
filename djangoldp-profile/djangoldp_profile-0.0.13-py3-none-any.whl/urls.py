"""djangoldp profile URL Configuration"""
from django.conf.urls import url, include

from djangoldp.permissions import AnonymousReadOnly
from djangoldp.views import LDPViewSet
from .models import Profile

urlpatterns = [
    url(r'^members/', LDPViewSet.urls(model=Profile, permission_classes=[AnonymousReadOnly])),
]

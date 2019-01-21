"""djangoldp circle URL Configuration"""
from django.conf.urls import url
from .models import Circle
from djangoldp.views import LDPViewSet

urlpatterns = [
    url(r'^circles/', LDPViewSet.urls(model=Circle, nested_fields=["team"])),
]

"""djangoldp joboffer URL Configuration"""
from django.conf.urls import url

from djangoldp.permissions import AnonymousReadOnly
from djangoldp.views import LDPViewSet
from .models import JobOffer

urlpatterns = [
    url(r'^job-offers/', LDPViewSet.urls(model=JobOffer, nested_fields=["skills"], permission_classes=[AnonymousReadOnly])),
]

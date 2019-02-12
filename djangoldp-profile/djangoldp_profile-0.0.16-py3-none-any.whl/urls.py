"""djangoldp profile URL Configuration"""
from django.conf.urls import url

from djangoldp.views import LDPViewSet
from .models import Profile

urlpatterns = [
    url(r'^members/', LDPViewSet.urls(model=Profile,
                                      fields=['@id', 'jabberID', 'user', 'available', 'bio', 'city', 'country', 'phone',
                                              'website'], permission_classes=())),
]

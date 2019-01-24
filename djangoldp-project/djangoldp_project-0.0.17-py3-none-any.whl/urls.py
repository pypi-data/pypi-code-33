"""djangoldp project URL Configuration"""
from django.conf.urls import url

from djangoldp.permissions import AnonymousReadOnly
from djangoldp.views import LDPViewSet

from .views import ProjectViewSet
from .models import Project, Customer

urlpatterns = [
    url(r'^projects/', ProjectViewSet.urls()),
    url(r'^customers/', LDPViewSet.urls(model=Customer, permission_classes=[AnonymousReadOnly])),
]

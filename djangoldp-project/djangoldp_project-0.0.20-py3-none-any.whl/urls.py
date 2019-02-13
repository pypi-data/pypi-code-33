"""djangoldp project URL Configuration"""
from django.conf.urls import url

from djangoldp.views import LDPViewSet
from .models import Customer, Member
from .views import ProjectViewSet

urlpatterns = [
    url(r'^projects/', ProjectViewSet.urls(fields=['@id', 'name', 'description', 'creationDate', 'team', 'businessProvider', 'businessProviderFee', 'number', 'members', 'customer', 'jabberID', 'jabberRoom'])),
    url(r'^project-members/', LDPViewSet.urls(model=Member)),
    url(r'^customers/', LDPViewSet.urls(model=Customer, permission_classes=[]))
]

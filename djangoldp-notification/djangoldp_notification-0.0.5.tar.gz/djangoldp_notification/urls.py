"""djangoldp_notifications URL Configuration"""
from django.conf.urls import url
from .models import Notification, Subscription
from djangoldp.views import LDPViewSet
#from djangoldp.permissions import InboxPermissions

urlpatterns = [
    url(r'^notifications/', LDPViewSet.urls(model=Notification)),# permissions_classes=(InboxPermissions,),)),
    url(r'^subscriptions/', LDPViewSet.urls(model=Subscription)),
]

from distutils.version import StrictVersion

import django
from django.conf.urls import url, include

from rest_framework.routers import DefaultRouter
from app.resources import UserViewSet, IssueViewSet

# Create a router and register our viewsets with it.
router = DefaultRouter()
router.register(r'users', UserViewSet)
router.register(r'issue', IssueViewSet)

# The API URLs are now determined automatically by the router.
# Additionally, we include the login URLs for the browsable API.
urlpatterns = [
    url(r'^', include(router.urls)),
]

if StrictVersion(django.get_version()) < StrictVersion('1.9'):
    from django.conf.urls import patterns

    urlpatterns = patterns('', *urlpatterns)

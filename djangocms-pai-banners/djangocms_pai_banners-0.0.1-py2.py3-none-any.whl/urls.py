from django.conf.urls import url
from rest_framework.urlpatterns import format_suffix_patterns

from .views import BannerViewSet


urlpatterns = [
    url(r'^$', BannerViewSet.as_view({'get': 'list'}) , name="banner_list"),
    url(r'^(?P<banner_pk>[0-9]+)/$', BannerViewSet.as_view({'get': 'retrieve'}), name="banner_detail"),
]

urlpatterns = format_suffix_patterns(urlpatterns)

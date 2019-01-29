from django.conf.urls import url

from ccc.common.views import ShortURLView

urlpatterns = [
    url(r'^short-url/$', ShortURLView.as_view(), name='beacons_short_url'),
]

from django.conf.urls import url

from .views import ConsumerViewSet, GroupViewSet


urlpatterns = [
    url(r'^consumers/$', ConsumerViewSet.as_view({'get': 'list'}), name="consumer-list"),
    url(r'^consumers/(?P<kong_consumer_id>[0-9A-Fa-f-]+)/$', ConsumerViewSet.as_view({'get': 'retrieve'}), name="consumer-detail"),

    url(r'^groups/$', GroupViewSet.as_view({'get': 'list'}), name="group-list"),
]

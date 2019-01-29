from django.conf.urls import url

urlpatterns = [
    # examples:
    url(r'^/search/(?P<area_code>\d{3})$', 'api.phones.views.search', name='api.phone.search'),
    url(r'^/add/$', 'api.phones.views.add', name='api.phone.add'),
    url(r'^/list/$', 'api.phones.views.list', name='api.phone.list'),
]

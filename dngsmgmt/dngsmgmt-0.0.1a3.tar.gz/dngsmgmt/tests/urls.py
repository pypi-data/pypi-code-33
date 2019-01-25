from django.conf.urls import include, url

import dngsmgmt.urls

urlpatterns = [
    url(r'^dngsmgmt/', include((dngsmgmt.urls, 'dngsmgmt'), namespace='dngsmgmt')),
]

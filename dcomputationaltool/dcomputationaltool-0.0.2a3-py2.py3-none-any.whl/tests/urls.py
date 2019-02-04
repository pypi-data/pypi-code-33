from django.conf.urls import include, url

import dcomputationaltool.urls

urlpatterns = [
    url(r'^dcomputationaltool/',
        include((dcomputationaltool.urls, 'dcomputationaltool'), namespace='dcomputationaltool')),
]

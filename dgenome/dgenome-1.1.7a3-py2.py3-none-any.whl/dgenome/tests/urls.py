from django.conf.urls import include, url

import dgenome.urls

urlpatterns = [
    url(r'^dgenome/', include((dgenome.urls, 'dgenome'), namespace='dgenome')),
]

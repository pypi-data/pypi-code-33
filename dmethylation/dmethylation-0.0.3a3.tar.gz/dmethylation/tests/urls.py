from django.conf.urls import include, url

import dmethylation.urls

urlpatterns = [
    url(r'^dmethylation/', include((dmethylation.urls, 'dmethylation'), namespace='dmethylation')),
]

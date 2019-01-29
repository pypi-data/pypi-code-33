from django.conf.urls import url

from ccc.tutorial.views import TutorialVideoList

urlpatterns = [
    url(r'^tutorial/$', TutorialVideoList.as_view(), name='tutorial'),
]

from django.conf.urls import url
from rest_framework.urlpatterns import format_suffix_patterns

from .views import ContactAPIView


urlpatterns = [
    url(r'^$', ContactAPIView.as_view(), name="contact"),
]

urlpatterns = format_suffix_patterns(urlpatterns)

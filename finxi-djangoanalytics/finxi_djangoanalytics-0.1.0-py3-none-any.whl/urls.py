from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^receive', views.AnalyticsProcessor.as_view()),
]
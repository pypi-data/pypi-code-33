from django.conf.urls import url
from generalobj import views

urlpatterns = [
    url('download_excelsheet', views.download_excelsheet, \
            name='download_excelsheet'),
]
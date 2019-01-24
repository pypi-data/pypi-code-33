from django.conf.urls import url

from views import mangopay_test


urlpatterns = [
    url(r'^$', mangopay_test, name="mangopay"),
   ]

from django.conf.urls import url

from mangopayments.views import mangopay_test

app_name = 'mangopay'

urlpatterns = [
    url(r'^$', mangopay_test, name="mangopay"),
   ]

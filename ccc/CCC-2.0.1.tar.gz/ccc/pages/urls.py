from django.conf.urls import url

from ccc.pages.views import ContactUsView, PricingView, home

app_name = 'pages'

urlpatterns = [
    url(r'^$', home, name='home'),
    url(r'^pricing/$', PricingView.as_view(), name='pricing'),
    url(r'^contact-us/$', ContactUsView.as_view(), name='contact_us'),
]

from django.conf.urls import url

from .views import login, complete, logout

urlpatterns = [
    url(r'^login/$',    login,      name='fas-login'),
    url(r'^complete/$', complete,   name='fas-complete'),
    url(r'^logout/$',   logout,     name='fas-logout'),
]

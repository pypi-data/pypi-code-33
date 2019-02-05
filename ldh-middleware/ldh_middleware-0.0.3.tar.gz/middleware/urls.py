"""middleware URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.11/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import include, url
from django.contrib import admin
from django.views.generic import RedirectView
from registration.backends.simple.views import RegistrationView

import limitmonitor.views
import purist.views
from ldapregister.forms import RegistrationForm

#
# Set admin titles for this site
#

admin.site.site_title = "Site administration"
admin.site.site_header = "Site administration"

#
# Define patterns for this site
#

urlpatterns = [
    url(r'^$', purist.views.home, name='home'),
    url(r'^admin/', admin.site.urls),
    url(r'^accounts/$', RedirectView.as_view(url='/')),
    url(r'^accounts/profile/$', limitmonitor.views.userlimit, name='profile'),
    url(r'^accounts/profile/purist.ovpn', limitmonitor.views.ovpn_userfile, name='ovpn_userfile'),
    url(r'^accounts/register/$', RegistrationView.as_view(form_class=RegistrationForm), name='registration_register'),
    url(r'^accounts/', include('registration.backends.simple.urls')),
    url(r'^download/', include('django_agpl.urls')),
    url(r'^jslicense/$', purist.views.jslicense, name='jslicense'),
]

from __future__ import absolute_import, division, print_function, unicode_literals

from django.conf.urls import url

from easymockups import views


app_name = 'easymockups'

urlpatterns = [url(r'^mockups/(?P<mockup_template_name>.+)', views.display_template, name='display_template'),
]
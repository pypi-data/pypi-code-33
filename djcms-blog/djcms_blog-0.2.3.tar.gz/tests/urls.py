from django.conf.urls import include, url
from django.conf.urls.i18n import i18n_patterns

from django.contrib.sitemaps.views import sitemap

urlpatterns = [
    url(r'^sitemap\.xml$', sitemap, name='sitemap-xml'),
]

urlpatterns += i18n_patterns(
    url(r'^', include('djcms_blog.urls')),
)

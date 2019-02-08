"""URL Configuration."""
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.staticfiles.views import serve
from django.http import HttpResponse
from django.urls import include, path


def build_urlpatterns(*paths):
    """
    Generate urlpatterns, adding URL_PREFIX, health checks, prometheus urls, and optional static files urls.

    Valid input is what would normally be assigned in urlpatterns

    ```
    paths = [
        path('', include('{project}.apps.{app}.urls'))
    ]
    ```
    """
    urlpatterns = [path(settings.URL_PREFIX, include(list(paths))), ]

    # Paths that check services health
    urlpatterns += [
        path('healthz', lambda request: HttpResponse(status=200), name='health-check'),
        path('readyz', lambda request: HttpResponse(status=200), name='ready-check'),
    ]

    # Prometheus paths
    urlpatterns += [path('', include('django_prometheus.urls')), ]

    # Include static file urls in development and when AWS S3 Storage is being used
    if settings.DEBUG and not settings.AWS_STORAGE:
        urlpatterns += static(settings.STATIC_URL, view=serve)

    return urlpatterns

from django.urls import path, re_path
from django.conf import settings
from rest_framework import permissions
from rest_framework.documentation import include_docs_urls
from drf_yasg.views import get_schema_view
from drf_yasg import openapi


def build_doc_urls(version=None):
    if not version:
        version = settings.DOCS_VERSION

    # Swagger
    schema_view = get_schema_view(
        openapi.Info(
            title=settings.DOCS_TITLE,
            default_version=version,
        ),
        validators=['flex', 'ssv'],
        public=True,
        permission_classes=(permissions.AllowAny,),
    )

    return [
        # Vanilla DRF Docs
        path('docs/', include_docs_urls(title=settings.DOCS_TITLE)),

        # Swagger Docs
        re_path(r'^swagger(?P<format>\.json|\.yaml)$', schema_view.without_ui(cache_timeout=None), name='schema-json'),
        path('swagger/', schema_view.with_ui('swagger', cache_timeout=None), name='schema-swagger-ui'),
        path('redoc/', schema_view.with_ui('redoc', cache_timeout=None), name='schema-redoc'),
    ]

from django.conf import settings
from django.urls.conf import path
from django.views.generic.base import RedirectView

from .admin_site import ambition_ae_admin

app_name = "ambition_ae"

urlpatterns = [
    path("admin/", ambition_ae_admin.urls),
    path("", RedirectView.as_view(url="admin/"), name="home_url"),
]


if settings.APP_NAME == "ambition_ae":
    from django.contrib import admin

    urlpatterns += [path("admin/", admin.site.urls)]

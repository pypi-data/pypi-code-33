from django.urls.conf import path
from django.conf import settings
from edc_base.views import HomeView

app_name = "edc_base"

urlpatterns = [path(r"", HomeView.as_view(), name="home_url")]

if settings.APP_NAME == "edc_base":
    from edc_base.tests.admin import edc_base_admin  # noqa

    urlpatterns += [path("admin/", edc_base_admin.urls)]

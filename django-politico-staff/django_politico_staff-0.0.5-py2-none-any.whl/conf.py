"""
Use this file to configure pluggable app settings and resolve defaults
with any overrides set in project settings.
"""

from django.conf import settings as project_settings
from django.utils.text import slugify

from staff.utils.importers import import_class


class Settings:
    pass


Settings.API_AUTHENTICATION_CLASS = import_class(
    getattr(
        project_settings,
        "STAFF_API_AUTHENTICATION_CLASS",
        "tokenservice.authentication.TokenAuthentication",
    )
)

Settings.API_PERMISSION_CLASS = import_class(
    getattr(
        project_settings,
        "STAFF_API_PERMISSION_CLASS",
        "rest_framework.permissions.IsAuthenticated",
    )
)


Settings.SLACK_API_TOKEN = getattr(
    project_settings, "STAFF_SLACK_API_TOKEN", None
)

Settings.SECRET_TOKEN = getattr(
    project_settings, "STAFF_SECRET_TOKEN", "SECRET"
)

Settings.AUTH_DECORATOR = getattr(
    project_settings,
    "STAFF_AUTH_DECORATOR",
    "django.contrib.admin.views.decorators.staff_member_required",
)


def default_user_image_upload_to(instance, filename):
    return "staff/{0}/{1}".format(
        slugify(f"{instance.user.first_name} {instance.user.last_name}"),
        filename,
    )


Settings.USER_IMAGE_UPLOAD_TO = getattr(
    project_settings,
    "STAFF_USER_IMAGE_UPLOAD_TO",
    default_user_image_upload_to,
)


settings = Settings

"""
Use this file to configure pluggable app settings and resolve defaults
with any overrides set in project settings.
"""

from django.conf import settings as project_settings


class Settings:
    pass


Settings.AUTH_DECORATOR = getattr(
    project_settings,
    "BASE_AUTH_DECORATOR",
    "django.contrib.admin.views.decorators.staff_member_required",
)


settings = Settings

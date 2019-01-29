"""
Use this file to configure pluggable app settings and resolve defaults
with any overrides set in project settings.
"""

from django.conf import settings as project_settings

from .exceptions import TrackerConfigError


class Settings:
    pass


Settings.AUTH_DECORATOR = getattr(
    project_settings,
    "TRACKER_AUTH_DECORATOR",
    "django.contrib.auth.decorators.login_required",
)

Settings.SECRET_KEY = getattr(
    project_settings, "TRACKER_SECRET_KEY", "a-bad-secret-key"
)

Settings.AWS_ACCESS_KEY_ID = getattr(
    project_settings, "TRACKER_AWS_ACCESS_KEY_ID", None
)

Settings.AWS_SECRET_ACCESS_KEY = getattr(
    project_settings, "TRACKER_AWS_SECRET_ACCESS_KEY", None
)

Settings.AWS_REGION = getattr(project_settings, "TRACKER_AWS_REGION", None)

Settings.AWS_S3_BUCKET = getattr(
    project_settings, "TRACKER_AWS_S3_BUCKET", None
)

Settings.CLOUDFRONT_ALTERNATE_DOMAIN = getattr(
    project_settings, "TRACKER_CLOUDFRONT_ALTERNATE_DOMAIN", None
)

Settings.S3_UPLOAD_ROOT = getattr(
    project_settings, "TRACKER_S3_UPLOAD_ROOT", "uploads/tracker"
)

Settings.TWITTER_CONSUMER_KEY = getattr(
    project_settings, "TRACKER_TWITTER_CONSUMER_KEY", None
)

Settings.TWITTER_CONSUMER_SECRET = getattr(
    project_settings, "TRACKER_TWITTER_CONSUMER_SECRET", None
)

Settings.TWITTER_ACCESS_TOKEN_KEY = getattr(
    project_settings, "TRACKER_TWITTER_ACCESS_TOKEN_KEY", None
)

Settings.TWITTER_ACCESS_TOKEN_SECRET = getattr(
    project_settings, "TRACKER_TWITTER_ACCESS_TOKEN_SECRET", None
)

Settings.TWITTER_WHITELIST = getattr(
    project_settings, "TRACKER_TWITTER_WHITELIST", []
)

settings = Settings

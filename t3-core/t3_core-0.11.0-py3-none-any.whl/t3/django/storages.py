# pylint: disable=W0223
from django.conf import settings
from storages.backends.s3boto3 import S3Boto3Storage


class MediaStorage(S3Boto3Storage):
    location = settings.MEDIAFILES_LOCATION
    bucket_name = settings.MEDIAFILES_BUCKET
    default_acl = 'private'


class StaticStorage(S3Boto3Storage):
    location = settings.STATICFILES_LOCATION
    bucket_name = settings.STATICFILES_BUCKET
    default_acl = 'public-read'

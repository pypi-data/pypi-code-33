from django.conf import settings
from django.db import models

from encrypted_model_fields.fields import EncryptedCharField


# TODO remove this model and depend on Katka-core API
class KatkaProject(models.Model):
    project_id = models.UUIDField(unique=True, null=False, blank=False)
    oauth_access_token = EncryptedCharField(max_length=100, null=True, blank=True)
    base_url = models.URLField(null=False, blank=False, default=settings.DEFAULT_BITBUCKET_SERVICE_LOCATION)

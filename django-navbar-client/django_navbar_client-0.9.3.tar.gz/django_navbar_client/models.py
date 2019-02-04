from django.conf import settings
from django.contrib.auth.models import User
from django.db import models
from uuid import uuid5,UUID

# Create your models here.
NIL = UUID("00000000000000000000000000000000")


class AuthProfile(models.Model):
    user = models.OneToOneField(User, models.CASCADE, primary_key=True)
    uuid = models.UUIDField(blank=True, default=NIL, editable=False)
    token = models.TextField()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def save(self, *args, **kwargs):
        if self.uuid == NIL:
            self.uuid = uuid5(settings.NAMESPACE_HOST_UUID, self.user.username)
        super().save(*args, **kwargs)

    def __str__(self):
        return "{0}::{1}".format(self.user.username, self.uuid)

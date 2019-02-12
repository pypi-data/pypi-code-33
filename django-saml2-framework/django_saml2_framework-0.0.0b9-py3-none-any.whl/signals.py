import os

from django.db import models
from django.dispatch.dispatcher import receiver

from .models import SpMetadata
from . import IDP

@receiver(models.signals.post_save, sender=SpMetadata)
def reload_idp_server(sender, instance, **kwargs):
    """
    todo: why is this signal here?  We may not :)
    """
    
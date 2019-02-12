import uuid

from django.db import models


class UndeliverableMessage(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    created_at = models.DateTimeField(auto_now_add=True)

    message_type = models.CharField(max_length=256)
    message_timestamp = models.DateTimeField()
    payload = models.TextField()
    queue = models.CharField(max_length=80)
    topic_arn = models.CharField(max_length=2048, null=True)

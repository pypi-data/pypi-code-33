from django.contrib.auth.models import User
from jsonfield import JSONField
from uuid import uuid4
from django.db import models


class TelegramBot(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    code = models.CharField(max_length=64, null=True, blank=True)
    plugin_name = models.CharField(max_length=255)
    token = models.CharField(max_length=255, unique=True)
    url_prefix = models.CharField(max_length=255, unique=True, null=True, blank=True)
    settings = JSONField(null=True, blank=True)
    owners = models.ManyToManyField(User)

    def save(self, force_insert=False, force_update=False, using=None,
             update_fields=None):
        if not self.url_prefix:
            self.url_prefix = None
        return super(TelegramBot, self).save(force_insert, force_update, using, update_fields)

    def __str__(self):
        return self.code if self.code else '{} [#{}]'.format(self.plugin_name, self.pk)


class BotAdminUser(models.Model):
    name = models.CharField(max_length=255)
    chat_id = models.CharField(max_length=255)

    def __str__(self):
        return '{} [chat_id: {}]'.format(self.name, self.chat_id)

from django.conf import settings
from django.db import models


class Number(models.Model):
    user = models.ForeignKey(settings.ACCOUNT_USER_PROXY_MODEL, related_name='numbers', on_delete=models.CASCADE)
    sid = models.CharField(max_length=100)
    phone_no = models.CharField(max_length=16)
    friendly_name = models.CharField(max_length=16)
    notes = models.CharField(max_length=200)

    def __str__(self):
        return self.friendly_name

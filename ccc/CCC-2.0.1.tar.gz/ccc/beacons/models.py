from django.conf import settings
from django.db import models


class Beacon(models.Model):
    name = models.CharField(max_length=255)
    uid = models.CharField(max_length=50)
    url = models.URLField(blank=True)
    user = models.ForeignKey(settings.ACCOUNT_USER_PROXY_MODEL, null=True, blank=True, on_delete=models.SET_NULL)
    is_active = models.BooleanField(default=True)
    created_on = models.DateTimeField(auto_now_add=True, blank=True, null=True)
    updated_on = models.DateTimeField(auto_now=True, blank=True, null=True)

    def __str__(self):
        return '%s -> %s (%s)' % (self.id, self.name, self.url)

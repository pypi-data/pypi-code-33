from django.conf import settings
from django.db import models

from generic.helpers import (get_uuid1, get_current_datetime)

User = settings.AUTH_USER_MODEL


class AuthToken(models.Model):
    """
    Overrides the default Django Token
    """
    id = models.UUIDField(default=get_uuid1, primary_key=True)
    refresh_key = models.CharField(max_length=500)
    user = models.ForeignKey(User, null=False, blank=False,
                             related_name='auth_token_set', on_delete=models.CASCADE)
    created = models.DateTimeField(null=False, blank=False, default=get_current_datetime)

    def __str__(self):
        return "{0}".format(self.id)

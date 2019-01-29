import datetime
import uuid

from django.conf import settings
from django.db import models
from django.db.models.signals import pre_save
from django.dispatch import receiver
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _


class AuthState(models.Model):
    user = models.ForeignKey(settings.ACCOUNT_USER_PROXY_MODEL, on_delete=models.CASCADE)
    code = models.CharField(max_length=100, default=uuid.uuid4().__str__()[:50])
    expires = models.DateTimeField(null=True, blank=True)
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.code


# The auth state code lasts for only 1hr
@receiver(pre_save, sender=AuthState)
def update_auth_state_expiry(sender, instance, **kwargs):
    instance.expires = timezone.now() + datetime.timedelta(hours=1)


ACCESS_TOKEN_TYPES = (
    (1, _('User')),
    (2, _('Page')),
    (3, _('Group')),
)

# Right now, we are not keeping page tokens atm, we are carrying the tokens around


class AccessToken(models.Model):
    user = models.ForeignKey(settings.ACCOUNT_USER_PROXY_MODEL, on_delete=models.CASCADE, null=True)
    facebook_uid = models.CharField(max_length=100, null=True, blank=True)
    permissions = models.TextField(null=True, blank=True)
    token = models.CharField(max_length=500)
    token_type = models.CharField(max_length=100, null=True)
    type = models.IntegerField(choices=ACCESS_TOKEN_TYPES, default=1)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    expires = models.DateTimeField(null=True)

    def set_expiry(self, seconds):
        self.expires = timezone.now() + datetime.timedelta(seconds=seconds)

    @property
    def is_valid(self):
        return self.expires >= timezone.now()

    def __str__(self):
        return self.token


PROFILE_TYPE = (
    (1, _('User')),
    (2, _('Page')),
    (3, _('Group')),
)


class FacebookProfile(models.Model):
    access_token = models.ForeignKey(AccessToken, null=True, on_delete=models.CASCADE)
    picture = models.URLField(blank=True, null=True)
    first_name = models.CharField(max_length=500, null=True)
    middle_name = models.CharField(max_length=500, null=True)
    last_name = models.CharField(max_length=500, null=True)
    about = models.CharField(max_length=500, null=True)
    link = models.URLField(null=True, max_length=3000)

    def __str__(self):
        return '{} {}'.format(self.first_name, self.last_name)

    @property
    def get_tasks(self):
        return self.tasks.split(',')

    @property
    def name(self):
        return '{} {} {}'.format(self.first_name, self.middle_name, self.last_name)

    def set_tasks(self, task_list):
        self.tasks = ','.join(task_list)

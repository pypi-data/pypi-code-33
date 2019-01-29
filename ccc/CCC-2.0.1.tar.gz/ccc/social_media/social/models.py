from django.conf import settings
from django.db import models
from django.utils.translation import ugettext as _


class Post(models.Model):
    user = models.ForeignKey(settings.ACCOUNT_USER_PROXY_MODEL, on_delete=models.CASCADE)
    location = models.CharField(max_length=500, null=True)
    content = models.TextField()
    media = models.FileField(upload_to='social/%d%m%y/')
    created = models.DateTimeField(auto_now_add=True)
    schedule_date = models.DateTimeField(null=True)

    def __str__(self):
        return self.content[:15] + '...'


TARGET_PLATFORMS_FOR_POSTS = (
    (1, _('Facebook Page')),
    (2, _('Facebook Group')),
    (3, _('Instagram')),
    (4, _('Twitter')),
    (5, _('LinkedIn')),
)


class PostedTo(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    target = models.IntegerField(choices=TARGET_PLATFORMS_FOR_POSTS, null=True)
    target_id = models.CharField(max_length=400, null=True)
    target_link = models.CharField(max_length=1000, null=True)
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return '{} to {}'.format(self.post.__str__(), self.get_target_display())

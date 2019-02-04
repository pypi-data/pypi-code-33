from django.contrib.auth.models import User
from django.db import models

from staff.conf import settings


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)

    # politico.com
    politico_title = models.CharField(
        max_length=100, blank=True, null=True, verbose_name="Title"
    )
    politico_author_page = models.URLField(
        blank=True, null=True, verbose_name="Author page"
    )

    # Slack
    slack_api_id = models.CharField(
        max_length=50, blank=True, null=True, verbose_name="ID"
    )
    slack_image = models.ImageField(
        upload_to=settings.USER_IMAGE_UPLOAD_TO,
        blank=True,
        null=True,
        verbose_name="Profile pic",
    )

    # Google
    google_email = models.EmailField(
        blank=True, null=True, verbose_name="Gmail"
    )
    google_display_name = models.CharField(
        max_length=250, blank=True, null=True, verbose_name="Display name"
    )

    # twitter
    twitter_handle = models.CharField(
        max_length=250, blank=True, null=True, verbose_name="Handle"
    )

    def __str__(self):
        return self.user.email

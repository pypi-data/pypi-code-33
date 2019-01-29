from django.conf import settings
from django.db import models
from django.urls import reverse


class DigitalVideo(models.Model):
    user = models.ForeignKey(settings.ACCOUNT_USER_PROXY_MODEL, on_delete=models.CASCADE)
    video = models.FileField(null=True, blank=True, upload_to="digital_assets/video")
    uploaded_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    video_name = models.CharField(max_length=100, null=True)

    def __str__(self):
        return self.video_name

    def get_absolute_url(self):
        return reverse("srm:digital-assets:video_update_url", args=([self.id]))

    def get_delete_url(self):

        return reverse("srm:digital-assets:video_delete_url", args=([self.id]))


class DigitalAudio(models.Model):
    user = models.ForeignKey(settings.ACCOUNT_USER_PROXY_MODEL, on_delete=models.CASCADE)
    audio = models.FileField(null=True, blank=True, upload_to="digital_assets/audio")
    uploaded_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    audio_name = models.CharField(max_length=100, null=True)

    def __str__(self):
        return self.audio_name

    def get_absolute_url(self):
        return reverse("srm:digital-assets:audio_update_url", args=([self.id]))

    def get_delete_url(self):
        return reverse("srm:digital-assets:audio_delete_url", args=([self.id]))


class DigitalImage(models.Model):
    user = models.ForeignKey(settings.ACCOUNT_USER_PROXY_MODEL, on_delete=models.CASCADE)
    image = models.ImageField(null=True, blank=True, upload_to="digital_assets/pictures")
    uploaded_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    image_name = models.CharField(max_length=100, null=True)

    class Meta:
        ordering = ['-id']

    def __str__(self):
        return self.image_name

    def get_absolute_url(self):
        return reverse("srm:digital-assets:image_update_url", args=([self.id]))

    def get_delete_url(self):
        return reverse("srm:digital-assets:image_delete_url", args=([self.id]))


class DigitalAttachment(models.Model):
    user = models.ForeignKey(settings.ACCOUNT_USER_PROXY_MODEL, on_delete=models.CASCADE)
    attachment = models.FileField(null=True, blank=True, upload_to="digital_assets/attachments")
    uploaded_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    attachment_name = models.CharField(max_length=100, null=True)

    def __str__(self):
        return self.attachment_name

    def get_absolute_url(self):
        return reverse("srm:digital-assets:attachment_update_url", args=([self.id]))

    def get_delete_url(self):
        return reverse("srm:digital-assets:attachment_delete_url", args=([self.id]))

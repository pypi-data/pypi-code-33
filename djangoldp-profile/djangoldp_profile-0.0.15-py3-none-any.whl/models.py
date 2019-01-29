from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.urlresolvers import reverse_lazy


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    available = models.NullBooleanField(blank=True)
    bio = models.CharField(max_length=255, blank=True, null=True)
    city = models.CharField(max_length=255, blank=True, null=True)
    country = models.CharField(max_length=255,  blank=True, null=True)
    phone = models.CharField(max_length=255, blank=True, null=True)
    website = models.URLField(blank=True)

    def jabberID(self):
        try:
            return self.user.chatProfile.jabberID
        except:
            return None

    class Meta:
        auto_author = 'user'
        permissions = (
            ('view_member', 'Read'),
            ('control_member', 'Control'),
        )

    def get_absolute_url(self):
        return reverse_lazy('profile-detail', kwargs={'pk': self.pk})


    def __str__(self):
        return '{} ({})'.format(self.user.get_full_name(), self.user.username)

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)
    else:
        instance.profile.save()

from django.db import models
from django.utils.translation import ugettext_lazy as _


class Contact(models.Model):

    class Meta:
        verbose_name = _('Contact')
        verbose_name_plural = _('Contacts')

    created_at = models.DateTimeField(auto_now_add=True)

    name = models.CharField(
        verbose_name=_('Name'),
        max_length=255
    )
    email = models.EmailField()
    message = models.TextField(
      verbose_name=_('Message'))

    def __str__(self):
        return self.email

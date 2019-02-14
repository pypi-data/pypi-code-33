from django.db import models
from django.utils.translation import ugettext_lazy as _
from filer.fields.image import FilerImageField


class Banner(models.Model):
  
    created_at = models.DateTimeField(auto_now_add=True)
  
    name = models.CharField(
        verbose_name=_('Name'),
        max_length=255
    )

    starts_on = models.DateTimeField(null=True)
    ends_on = models.DateTimeField(null=True, blank=True)

    image = FilerImageField(verbose_name=_('Image'), null=True, blank=True, related_name='banner_image')
    code = models.TextField(blank=True, null=True)
    
    url = models.URLField(null=True, blank=True)
    
    value = models.PositiveIntegerField(default=0)

    class Meta:
        verbose_name = _('Banner')
        verbose_name_plural = _('Banners')
        ordering = ['-value', '-starts_on']

    def __str__(self):
        return self.name

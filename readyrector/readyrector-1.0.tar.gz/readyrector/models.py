from django.db import models
from django.utils.translation import gettext_lazy as _

from readyrector.validators import PathOrURLValidator


class Redirect(models.Model):
    from_path = models.CharField(_('from path'), max_length=250, unique=True)
    to_url = models.CharField(_('to URL'), max_length=250, validators=[
        PathOrURLValidator(schemes=('http', 'https'))
    ])
    hits = models.PositiveIntegerField(
        _('number of hits'), editable=False, default=0)
    last_hit = models.DateTimeField(
        _('latest hit'), editable=False, null=True, blank=True)

    class Meta:
        verbose_name = _('redirect')
        verbose_name_plural = _('redirects')
        ordering = ('from_path',)

    def __str__(self):
        return str(self.from_path)

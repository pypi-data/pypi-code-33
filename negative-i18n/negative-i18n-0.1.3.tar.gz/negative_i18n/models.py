from django.conf import settings
from django.db import models

from django.core.cache import cache


class StringTranslation(models.Model):
    last_used = models.DateTimeField(default=None, blank=True, null=True)

    context = models.CharField(max_length=50, null=True, blank=True, default='default')
    key = models.CharField(max_length=400, null=True, blank=True)

    translation = models.TextField(blank=True, null=True)

    obsolete = models.BooleanField(default=False)

    def __str__(self):
        return '%s%s' % (self.key, (' (%s)' % self.context) if self.context else '')

    class Meta:
        unique_together = (('context', 'key'),)
        # verbose_name = 'Перевод строки'
        # verbose_name_plural = 'Переводы строк'

    def save(self, force_insert=False, force_update=False, using=None, update_fields=None):
        super().save(force_insert, force_update, using, update_fields)

        cache.delete_many(
            ['translations_{}'.format(lang) for lang, name in settings.LANGUAGES]
        )




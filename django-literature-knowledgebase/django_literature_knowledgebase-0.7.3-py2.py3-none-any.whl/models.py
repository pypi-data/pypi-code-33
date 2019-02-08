# -*- coding: utf-8 -*-
import os

from django.conf import settings
from django.contrib.contenttypes.fields import GenericRelation
from django.db import models
from django.utils.translation import ugettext_lazy as _

from model_utils.models import TimeStampedModel

from . import choices, managers, utils


def file_path(instance, filename):
    return 'article-pdfs/{0}'.format(filename)


class Article(TimeStampedModel):
    """Article from NCBI. PubMed or PMC."""

    source = models.SmallIntegerField(
        choices=choices.SOURCES,
        default=choices.SOURCES.pubmed
    )
    file = models.FileField(upload_to=file_path, blank=True, null=True)
    identifier = models.IntegerField(db_index=True)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        blank=True,
        null=True
    )
    active = models.BooleanField(default=True)
    description = models.CharField(max_length=255, blank=True)
    comments = GenericRelation('user_activities.Comment')

    objects = managers.ArticleQuerySet.as_manager()

    class Meta:
        verbose_name = _('Article')
        verbose_name_plural = _('Articles')
        unique_together = ('source', 'identifier')

    def __str__(self):
        return '{0}: {1}'.format(self.get_source_display(), self.identifier)

    @property
    def article_url(self):
        return utils.build_article_url(self.identifier, self.get_source_display())

    @property
    def fetch_url(self):
        return utils.build_efetch_url(self.identifier, self.get_source_display())

    @property
    def summary_url(self):
        return utils.build_esummary_url(self.identifier, self.get_source_display())

    @property
    def file_url(self):
        return os.path.join(settings.MEDIA_URL, str(self.file))

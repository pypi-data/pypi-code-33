from adminsortable.models import SortableMixin
from django.conf import settings
from django.db import models
from embed_video.fields import EmbedVideoField
from redactor.fields import RedactorField


class Video(SortableMixin):
    title = models.CharField(max_length=250, verbose_name=u'Title', blank=True, null=True)
    description = RedactorField(verbose_name=u'Description', blank=True, null=True)
    faqs = RedactorField(verbose_name=u'Questions answered', blank=True, null=True)
    video = EmbedVideoField()  # same like models.URLField()
    user = models.ForeignKey(settings.ACCOUNT_USER_PROXY_MODEL, blank=True, null=True, on_delete=models.SET_NULL)
    category = models.CharField(max_length=250, choices=(('1', 'How TO'), ('2', 'Membership')),
                                verbose_name=u'Category', blank=True, null=True)
    access = models.CharField(max_length=250, choices=(('1', 'Registered Only'),
                                                       ('2', 'Everybody')), verbose_name=u'Access Level', blank=True,
                              null=True)

    date_created = models.DateTimeField(auto_now_add=True)
    date_updated = models.DateTimeField(auto_now=True)

    in_popup = models.BooleanField(blank=True, default=False)

    # define the field the model should be ordered by
    ordering = models.PositiveIntegerField(default=0, editable=False, db_index=True)

    def __str__(self):
        return self.title

    class Meta:
        ordering = ('ordering',)

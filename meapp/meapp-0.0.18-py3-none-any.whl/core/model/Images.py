from django.db import models
import uuid

from django.conf import settings
from ..fields.images import ImageField
HOST = settings.MEDIA_HOST

Default_IMAGE = '%sfine_uploader/head1.jpg' % settings.STATIC_URL
class BaseImageModel(models.Model):
    @classmethod
    def default_url(cls):
        return Default_IMAGE

    filename = models.CharField(max_length=100,verbose_name='文件名')
    image = ImageField(upload_to='img/%Y/%m/%d')

    def _url(self):
        try:
            if self.image.url:
                return HOST + self.image.url
            return Default_IMAGE
        except Exception as e:
            return self.image.url
    url = property(_url)

    class Meta:
        ordering = ['id']
        abstract = True

    def save(self, force_insert=False, force_update=False, using=None,
             update_fields=None):
        self.filename = uuid.uuid4()
        super(BaseImageModel,self).save(force_insert=force_insert,force_update=force_update,using=using,update_fields=update_fields)


class ImageModel(BaseImageModel):
    pass
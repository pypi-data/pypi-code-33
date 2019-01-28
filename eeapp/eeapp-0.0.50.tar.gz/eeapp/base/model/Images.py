from django.db import models

# Create your models here.
from django.db import models

import uuid

# -*- coding: UTF-8 -*-
from django.core.files.storage import FileSystemStorage


class ImageStorage(FileSystemStorage):
    from django.conf import settings

    def __init__(self, location=settings.MEDIA_ROOT, base_url=settings.MEDIA_URL):
        # 初始化
        super(ImageStorage, self).__init__(location, base_url)

    # 重写 _save方法
    def _save(self, name, content):
        import os, time, random
        # 文件扩展名
        ext = os.path.splitext(name)[1]
        # 文件目录
        d = os.path.dirname(name)
        # 定义文件名，年月日时分秒随机数
        fn = time.strftime('%Y%m%d%H%M%S')
        fn = fn + '_%d' % random.randint(0, 100)
        # 重写合成文件名
        name = os.path.join(d, fn + ext)
        # 调用父类方法
        return super(ImageStorage, self)._save(name, content)
#
# try:
#     from eeapp.eeapp.model.Images import ImageModel
# except:
#     from ...eeapp.eeapp.model.Images import ImageModel


from django.conf import settings
Default_IMAGE = '%sfine_uploader/head1.jpg' % settings.STATIC_URL

from django.conf import settings
HOST = settings.MEDIA_HOST
class ImageModel(models.Model):
    @classmethod
    def default_url(cls):
        return Default_IMAGE

    filename = models.CharField(max_length=100,verbose_name='文件名')
    image = models.ImageField(upload_to='img/%Y/%m/%d',storage=ImageStorage())


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

    def save(self, force_insert=False, force_update=False, using=None,
             update_fields=None):

        iuuid = uuid.uuid4()
        self.filename = iuuid
        super(ImageModel,self).save(force_insert=force_insert,force_update=force_update,using=using,update_fields=update_fields)









# -*- coding: UTF-8 -*-
from django.db import models
from django.core.files.images import ImageFile
from django.core.files.storage import FileSystemStorage
from django.conf import settings


class ImageStorage(FileSystemStorage):

    def __init__(self, location=settings.MEDIA_ROOT, base_url=settings.MEDIA_URL):
        # 初始化
        super(ImageStorage, self).__init__(location, base_url)

    # 重写 _save方法
    def _save(self, name, content):
        import os, time, random

        file = ImageFile(content)
        width = file.width
        height = file.height

        # 文件扩展名
        ext = os.path.splitext(name)[1]
        # 文件目录
        d = os.path.dirname(name)
        # 定义文件名，年月日时分秒随机数
        fn = time.strftime('%Y%m%d%H%M%S')
        fn = fn + '_%d' % random.randint(0, 100)
        fn = fn + "@%dX%d" %(width,height)
        # 重写合成文件名
        name = os.path.join(d, fn + ext)

        # 调用父类方法
        return super(ImageStorage, self)._save(name, content)

    def url(self, name):
        url = super(ImageStorage,self).url(name)
        host = settings.MEDIA_HOST or ''

        return host + url


class ImageField(models.ImageField):
    def __init__(self, verbose_name=None, name=None, width_field=None, height_field=None, **kwargs):
        self.width_field, self.height_field = width_field, height_field
        kwargs['storage'] = ImageStorage()
        super().__init__(verbose_name, name, **kwargs)
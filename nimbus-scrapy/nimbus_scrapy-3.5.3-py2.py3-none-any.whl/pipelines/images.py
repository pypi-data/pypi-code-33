# -*- coding: utf-8 -*-
from __future__ import absolute_import, print_function, division, unicode_literals
import os
import hashlib
from twisted.internet.defer import Deferred, DeferredList
from twisted.python.failure import Failure
from scrapy.utils.misc import md5sum
from scrapy.utils.misc import arg_to_iter
from scrapy.utils.python import to_bytes
from scrapy.http import Request
from scrapy.settings import Settings
from scrapy.exceptions import DropItem
from scrapy.pipelines.images import ImagesPipeline as SCImagesPipeline


class ImagesPipeline(SCImagesPipeline):
    IMAGES_PATH_FIELD = "image_path"

    def __init__(self, store_uri, download_func=None, settings=None):
        super(ImagesPipeline, self).__init__(store_uri, settings=settings,
                                             download_func=download_func)
        self.images_path_field = settings.get('IMAGES_PATH_FIELD', self.IMAGES_PATH_FIELD)

    @classmethod
    def from_settings(cls, settings):
        s3store = cls.STORE_SCHEMES['s3']
        s3store.AWS_ACCESS_KEY_ID = settings['AWS_ACCESS_KEY_ID']
        s3store.AWS_SECRET_ACCESS_KEY = settings['AWS_SECRET_ACCESS_KEY']
        s3store.POLICY = settings['IMAGES_STORE_S3_ACL']

        gcs_store = cls.STORE_SCHEMES['gs']
        gcs_store.GCS_PROJECT_ID = settings['GCS_PROJECT_ID']

        store_uri = settings['IMAGES_STORE']
        return cls(store_uri, settings=settings)

    def process_item(self, item, spider):
        info = self.spiderinfo
        requests = arg_to_iter(self.get_media_requests(item, info))
        if not requests:
            return item
        dlist = [self._process_request(r, info) for r in requests]
        dfd = DeferredList(dlist, consumeErrors=1)
        return dfd.addCallback(self.item_completed, item, info)

    def get_media_requests(self, item, info):
        _urls = item.get(self.images_urls_field, [])
        _urls = arg_to_iter(_urls)
        _images_count = len(_urls)
        return [Request(x, meta={"images_path": item.get(self.images_path_field, ""), "images_count": _images_count})
                for x in _urls]

    def file_path(self, request, response=None, info=None):
        url = request.url
        _images_path = request.meta.get("images_path", None)
        _images_count = request.meta.get("images_count", 1)
        if not _images_path:
            image_guid = hashlib.sha1(to_bytes(url)).hexdigest()  # change to request.url after deprecation
            return 'full/{}.jpg'.format(image_guid)
        if _images_count == 1:
            name, ext = os.path.splitext(_images_path)
            if not ext:
                _, ext = os.path.splitext(request.url)
            return 'full/{}{}'.format(name, ext)
        else:
            name = request.url.split('/')[-1]
            return 'full/{}/{}'.format(_images_path, name)

    def thumb_path(self, request, thumb_id, response=None, info=None):
        url = request.url
        _images_path = request.meta.get("images_path", None)
        _images_count = request.meta.get("images_count", 1)
        if not _images_path:
            thumb_guid = hashlib.sha1(to_bytes(url)).hexdigest()  # change to request.url after deprecation
            return 'thumbs/{}/{}.jpg'.format(thumb_id, thumb_guid)
        if _images_count == 1:
            name, ext = os.path.splitext(_images_path)
            if not ext:
                _, ext = os.path.splitext(request.url)
            return 'thumbs/{}/{}{}'.format(thumb_id, name, ext)
        else:
            name = request.url.split('/')[-1]
            return 'thumbs/{}/{}/{}'.format(thumb_id, _images_path, name)




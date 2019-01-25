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
from scrapy.pipelines.files import FilesPipeline as SCFilesPipeline


class FilesPipeline(SCFilesPipeline):
    FILES_PATH_FIELD = "file_path"

    def __init__(self, store_uri, download_func=None, settings=None):
        super(FilesPipeline, self).__init__(store_uri, settings=settings,
                                            download_func=download_func)
        self.files_path_field = settings.get('FILES_PATH_FIELD', self.FILES_PATH_FIELD)

    @classmethod
    def from_settings(cls, settings):
        s3store = cls.STORE_SCHEMES['s3']
        s3store.AWS_ACCESS_KEY_ID = settings['AWS_ACCESS_KEY_ID']
        s3store.AWS_SECRET_ACCESS_KEY = settings['AWS_SECRET_ACCESS_KEY']
        s3store.POLICY = settings['FILES_STORE_S3_ACL']

        gcs_store = cls.STORE_SCHEMES['gs']
        gcs_store.GCS_PROJECT_ID = settings['GCS_PROJECT_ID']

        store_uri = settings['FILES_STORE']
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
        _urls = item.get(self.files_path_field, [])
        _urls = arg_to_iter(_urls)
        _files_count = len(_urls)
        return [Request(x, meta={"files_path": item.get(self.files_path_field, ""), "files_count": _files_count})
                for x in _urls]

    def file_path(self, request, response=None, info=None):
        url = request.url
        _files_path = request.meta.get("files_path", None)
        _files_count = request.meta.get("files_count", 1)
        if not _files_path:
            image_guid = hashlib.sha1(to_bytes(url)).hexdigest()  # change to request.url after deprecation
            return 'full/{}.jpg'.format(image_guid)
        if _files_count == 1:
            name, ext = os.path.splitext(_files_path)
            if not ext:
                _, ext = os.path.splitext(request.url)
            return 'full/{}{}'.format(name, ext)
        else:
            name = request.url.split('/')[-1]
            return 'full/{}/{}'.format(_files_path, name)





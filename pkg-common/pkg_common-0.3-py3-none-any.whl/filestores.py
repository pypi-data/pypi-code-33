# -*- coding: utf-8 -*-

from scrapy.pipelines.files import S3FilesStore


class CustomS3FilesStore(S3FilesStore):
    POLICY = 'public-read'
    HEADERS = {
        'Cache-Control': 'max-age=172800',
        'Content-Type': 'application/pdf',
        'Content-Disposition': 'inline'
    }
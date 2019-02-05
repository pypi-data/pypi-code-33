# -*- coding: utf-8 -*-

import scrapy
import logging
import pymongo

from scrapy.exceptions import DropItem
from scrapy.pipelines.files import FilesPipeline
from .filestores import CustomS3FilesStore


class PDFPipeline(FilesPipeline):
    def __init__(self, *args, **kwargs):
        self.STORE_SCHEMES['s3'] = CustomS3FilesStore
        super(PDFPipeline, self).__init__(*args, **kwargs)

    def get_media_requests(self, item, info):
        if 'file_urls' in item:
            for url in item['file_urls']:
                request = scrapy.Request(url=url)
                request.meta['directory'] = item['s3_directory']
                request.meta['file_name'] = item['unique_control']
                yield request

    def file_path(self, request, response=None, info=None):
        return request.meta.get('directory', '') + "/" + request.meta.get('file_name', '') + ".pdf"


class MongoDBPipeline(object):
    def __init__(self, mongo_uri):
        self.mongo_uri = mongo_uri

    @classmethod
    def from_crawler(cls, crawler):
        return cls(
            mongo_uri=crawler.settings.get('MONGO_URI'),
        )

    def open_spider(self, spider):
        self.client = pymongo.MongoClient(self.mongo_uri)

    def close_spider(self, spider):
        self.client.close()

    def process_item(self, item, spider):
        valid = True
        for data in item:
            if not data:
                raise DropItem("Missing {0}!".format(data))
        if valid:
            query = {"unique_control": item['unique_control']}
            dbname = ''.join([item['organization'], '_DBNAME'])

            data = dict(item)
            del data['organization']

            newvalues = {"$set": data}
            self.client[dbname][spider.custom_settings.get('COLLECTION_NAME')].update_one(query, newvalues,
                                                                                                       upsert=True)
            logging.log(logging.DEBUG, "Ticket added to MongoDB database!")
        return item

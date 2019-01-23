# -*- coding: utf-8 -*-
from __future__ import absolute_import, print_function, division, unicode_literals
import os
import sys

__all__ = [
    "default_settings",
    "update_settings",
]

DEFAULT_ITEM_PIPELINES = {
    'nimbus_scrapy.pipelines.files.FilesPipeline': 1,
    'nimbus_scrapy.pipelines.images.ImagesPipeline': 2,
    'nimbus_scrapy.pipelines.item.ItemPipeline': 300,
    'nimbus_scrapy.pipelines.callback.CallbackPipeline': 400,
}

DEFAULT_SPIDER_MIDDLEWARES = {
    'nimbus_scrapy.middlewares.DeltaFetch': 100,
}

DEFAULT_EXTENSIONS = {
    'nimbus_scrapy.extensions.spend.SpendStats': 0,
}

DEFAULT_REDIS_CONFIG = {
    "host": '127.0.0.1',
    "port": 6379,
    "db": 3,
    "password": None
}


def default_settings(**kwargs):
    default = {
        "BOT_NAME": "DEFAULT",
        "LOG_ENABLED": True,
        "LOG_LEVEL": "INFO",
        "DOWNLOAD_DELAY": 5,
        "ROBOTSTXT_OBEY": True,
        'TELNETCONSOLE_ENABLED': False,
        "DELTAFETCH_ENABLED": False,
        "DELTAFETCH_RESET": False,
        "DELTAFETCH_FLUSH": False,
        "DELTAFETCH_REDIS": DEFAULT_REDIS_CONFIG,
        "USER_AGENT": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.13; rv:61.0) Gecko/20100101 Firefox/61.0",
        "CLOSESPIDER_TIMEOUT": 0,
        "CLOSESPIDER_PAGECOUNT": 0,
        "CLOSESPIDER_ITEMCOUNT": 0,
        "CLOSESPIDER_ERRORCOUNT": 0,
        "PROCESS_ITEM_ENABLED": True,
        "ITEM_CALLBACK": None,
        "ITEM_CALLBACK_LOCK": False,
        "FILES_STORE": None,
        "FILES_URLS_FIELD":  "file_urls",
        "FILES_PATH_FIELD": "file_path",
        "FILES_RESULT_FIELD": "files",
        "IMAGES_STORE": None,
        "IMAGES_URLS_FIELD": "image_urls",
        "IMAGES_PATH_FIELD": "image_path",
        "IMAGES_RESULT_FIELD": "images",
        "MEDIA_ALLOW_REDIRECTS": True,
        "FILES_EXPIRES": 90,
        "IMAGES_EXPIRES": 90,
        "IMAGES_THUMBS": {
            'small': (128, 128),
            'big': (270, 270),
        },
        "SPEND_STATS_ENABLED": True,
    }
    default.update(kwargs)
    return default


def update_settings(settings=None):
    if settings is None:
        settings = {}
    _pipelines = settings.get("ITEM_PIPELINES", {})
    _pipelines.update(DEFAULT_ITEM_PIPELINES)
    _middlewares = settings.get("SPIDER_MIDDLEWARES", {})
    _middlewares.update(DEFAULT_SPIDER_MIDDLEWARES)
    _extensions = settings.get("EXTENSIONS", {})
    _extensions.update(DEFAULT_EXTENSIONS)
    settings["ITEM_PIPELINES"] = _pipelines
    settings["SPIDER_MIDDLEWARES"] = _middlewares
    settings["EXTENSIONS"] = _extensions
    return settings

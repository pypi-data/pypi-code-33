from mongobj.document import Document

from datetime import datetime

import pymongo


class Container(Document):
    __version__ = '1.0.0'
    __fields__ = [
        'name',
        'description'
    ]


class MediaFile(Document):
    __version__ = '1.0.0'
    __fields__ = [
        'container',
        'key',
        'url',
        'uploaded_on',
        'updated_on',
        'mimetype',
        'size',
        'info'
    ]
    __autos__ = {
        'updated_on': datetime.utcnow
    }


class MediaFileCache(Document):
    __version__ = '1.0.0'
    __fields__ = [
        'cache_key',
        'container',
        'key',
        'url'
    ]


def init(db):
    Container.set_collection(db.instance.get('media_containers'))

    MediaFile.set_collection(db.instance.get('media_files'))
    MediaFile.__collection__.create_index([
        ('container', pymongo.ASCENDING),
        ('key', pymongo.ASCENDING)
    ])

    MediaFileCache.set_collection(db.instance.get('media_file_cache'))

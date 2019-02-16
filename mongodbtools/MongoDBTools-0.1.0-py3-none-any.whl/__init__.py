try:
    import pymongo
except ImportError:
    from mongodbtools.exceptions import MissingPyMongoError
    raise MissingPyMongoError()

from mongodbtools.mongoconnection import MongoConnection
from mongodbtools.links import *

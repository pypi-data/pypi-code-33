"""
MongoDB Module

:version 0.0.5
"""

import pymongo
import time
from bson.objectid import ObjectId
from MongoExceptions import *


class Mongo:
    # Default URL
    url = "mongodb://127.0.0.1:27017/"

    # Connection
    Client = object

    # Database
    Database = object

    '''
    Constructor

    :param host: Database host
    :param port: Database port
    :param auth: Database Authentication
    :param username: Database username
    :param password: Database password
    '''

    def __init__(self, host="127.0.0.1", port=27017, auth=False, username="root", password="root", database="test"):

        if type(host) != str or type(port) != int \
                or type(auth) != bool or type(username) != str \
                or type(password) != str or type(database) != str:
            raise InvalidArgumentsException()

        if auth:
            self.url = "mongodb://{}:{}@{}:{}/".format(username, password, host, port)
        else:
            self.url = "mongodb://{}:{}/".format(host, port)

        self.Client = pymongo.MongoClient(self.url, serverSelectionTimeoutMS=100)

        try:
            databases = self.Client.list_database_names()
        except:
            raise ConnectFailedException()

        if database not in databases:
            raise NoDatabaseException()

        self.Database = self.Client[database]

    '''
    find

    :param collection: Database collection
    :param finddict: Query dict

    :return List
    '''

    def find(self, collection="test", finddict={}):

        if type(collection) != str:
            raise InvalidCollectionException()

        if type(finddict) != dict:
            raise InvalidQueryObjectException()

        collections = self.Database.list_collection_names()

        if collection not in collections:
            raise InvalidCollectionException()

        Collection = self.Database[collection]
        Cursor = Collection.find(finddict)
        result = []

        for data in Cursor:
            result.append(data)

        return result

    '''
    insert

    :param collection: Database collection
    :param insertObject: List or Dict

    :return List
    '''

    def insert(self, collection="test", insertObject=None):

        if type(collection) != str:
            raise InvalidCollectionException()

        if type(insertObject) != dict and type(insertObject) != list:
            raise InvalidInsertObjectException()

        if type(insertObject) == list:
            for i in range(0, len(insertObject)):
                if type(insertObject[i]) != dict:
                    raise InvalidInsertObjectException()

        collections = self.Database.list_collection_names()

        if collection not in collections:
            raise InvalidCollectionException()

        Collection = self.Database[collection]
        result = []

        if type(insertObject) == dict:
            temp = Collection.insert_one(insertObject)
            result.append(temp.inserted_id)

        if type(insertObject) == list:
            temp = Collection.insert_many(insertObject)
            for i in range(0, len(temp.inserted_ids)):
                result.append(temp.inserted_ids[i])

        return result

    '''
    remove

    :param collection: Database collection
    :param removeQuery: Remove Query
    :param removeAllConfirm: Confirm remove all data

    :return int
    '''

    def remove(self, collection="test", removeQuery=None, removeAllConfirm=False, removeMany=False):

        if type(collection) != str:
            raise InvalidCollectionException()

        if type(removeQuery) != dict:
            raise InvalidRemoveQueryException()

        if type(removeMany) != bool or type(removeAllConfirm) != bool:
            raise InvalidRemoveOptionException()

        collections = self.Database.list_collection_names()

        if collection not in collections:
            raise InvalidCollectionException()

        Collection = self.Database[collection]
        result = 0

        if not removeQuery:
            if not removeAllConfirm:
                raise RemoveAllNotConfirmedException()
            else:
                try:
                    result = Collection.delete_many({})
                except:
                    raise OperationFailedException()
        elif removeMany:
            try:
                result = Collection.delete_many(removeQuery)
            except:
                raise OperationFailedException()
        else:
            try:
                result = Collection.delete_one(removeQuery)
            except:
                raise OperationFailedException()

        return result.deleted_count

    '''
    update

    :param collection: Database collection
    :param updateQuery: Update Query
    :param updateDict: Update Dict
    :param updateMany: Update Many

    :return int
    '''

    def update(self, collection="test", updateQuery=None, updateDict=None, updateMany=False):

        if type(collection) != str:
            raise InvalidCollectionException()

        if type(updateQuery) != dict:
            raise InvalidUpdateQueryException()

        if type(updateDict) != dict:
            raise InvalidUpdateDictException()

        if type(updateMany) != bool:
            raise InvalidUpdateOptionException()

        collections = self.Database.list_collection_names()

        if collection not in collections:
            raise InvalidCollectionException()

        Collection = self.Database[collection]
        result = 0

        if updateMany:
            try:
                result = Collection.update_many(updateQuery, updateDict)
            except:
                raise OperationFailedException()
        else:
            try:
                result = Collection.update_one(updateQuery, updateDict)
            except:
                raise OperationFailedException()

        return result.modified_count

    '''
    ObjectId2UnixTimeStamp

    :param objectid: str or ObjectId

    :return float
    '''

    @staticmethod
    def ObjectId2UnixTimeStamp(objectid=None):

        if type(objectid) == ObjectId:
            result = time.mktime(objectid.generation_time.timetuple())
        elif type(objectid) == str:
            try:
                temp = ObjectId(objectid)
                result = time.mktime(temp.generation_time.timetuple())
            except:
                raise InvalidObjectIdException()
        else:
            raise InvalidObjectIdException()

        return result

    '''
    ObjectId2String

    :param objectid: ObjectId

    :return str
    '''

    @staticmethod
    def ObjectId2String(objectid):

        if type(objectid) != ObjectId:
            raise InvalidObjectIdException()

        return objectid.__str__()

    '''
    String2ObjectId

    :param objectid: str

    :return ObjectId
    '''

    @staticmethod
    def String2ObjectId(objectid=None):

        if type(objectid) != str:
            raise InvalidObjectIdException()

        try:
            result = ObjectId(objectid)
        except:
            raise InvalidObjectIdException()

        return result

import pymongo
from pymongo import MongoClient
import configparser
import json
from uuid import UUID
from bson import ObjectId

class JSONEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, UUID):
            # if the obj is uuid, we simply return the value of uuid
            #return obj.hex
            return str(obj)
        elif isinstance(obj, ObjectId):
            return str(obj)
        return json.JSONEncoder.default(self, obj)

class MongoDBDataHelper():

    def __init__(
        self, 
        logger=None,
        config_file='go_servers.ini',
        host_name='DataPlatform_DEV_ReadOnly'):
        self.logger = logger
        self.config_file = config_file
        self.host_name = host_name
        self.connect()

    def connect(self):
        self.config = configparser.ConfigParser()
        self.config.read(self.config_file)

        if 'AuthMech' in self.config[self.host_name]:
            self.client = MongoClient(
                host=self.config[self.host_name]['Server'], 
                username=self.config[self.host_name]['Username'],
                password=self.config[self.host_name]['Password'],
                port=int(self.config[self.host_name]['PORT']),
                authSource=self.config[self.host_name]['Database'],
                authMechanism=self.config[self.host_name]['AuthMech'])
        else:
            self.client = MongoClient(
                host=self.config[self.host_name]['Server'], 
                port=int(self.config[self.host_name]['PORT']))
        if self.logger != None:
            self.logger.info('client = %s' % self.client)

        if 'Database' in self.config[self.host_name]:
            self.db = self.client[self.config[self.host_name]['Database']]
        else:
            self.db = None

        return self.client, self.db

    def get_collection(self, collection):
        return self.db[collection]

    def find(self, collection, condition):
        self.logger_info('start finding result for ... ')
        self.logger_info('\tdb = %s' % self.db)
        self.logger_info('\tcollection = %s' % collection)
        self.logger_info('\tcondition = %s' % condition)

        cursor = self.db[collection].find(condition)

        result = []
        for c in cursor:
            # make UUID and ObjectID JSON serializable
            result.append(json.loads(json.dumps(c, cls=JSONEncoder)))

        self.logger_info('result.count = %s' % len(result))
        if len(result) > 0:
            self.logger_info('result[0] = %s' % result[0])

        return result

    def logger_info(self, msg):
        if self.logger != None:
            self.logger.info(msg)

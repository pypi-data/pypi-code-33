import pymongo

class a:
    def n(self):
        print("A")

def create_mongodb_connection(host, port):
    return pymongo.MongoClient('mongodb://%s:%d/' % (host, port))
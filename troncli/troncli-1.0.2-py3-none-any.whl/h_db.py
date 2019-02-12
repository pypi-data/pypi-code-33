from pymongo import MongoClient

class DB:
    """handler for db manage"""

    async def create(self):
        client = MongoClient('localhost', 27017)
        db = client.events

        # client = MongoClient('localhost',
        #                      18890,
        #                      username='admin',
        #                      password='',
        #                      authSource='admin')

        # client.admin.authenticate('siteRootAdmin', '')
        # client.testdb.add_user('user1', '12345678', True)


        # db = client.admin

        print('Database: ', db.name)
        print('Collection: ', db.my_collection)
        print('User: ', db.user)
        
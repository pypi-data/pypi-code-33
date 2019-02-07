from pyArango.connection import *

class Database:
    def __init__(self, name='DRE'):
        self.connection = Connection(username="root")
        self.root = self.connection.createDatabase(name=name)
        self.cols = {
            'publications': self.root.createCollection(name="Publications"),
            'diploma': self.root.createCollection(name="Diplomas"),
            'doctype': self.root.createCollection(name="DiplomaTypes"),
        }

    def add_publication(self, publication):
        collection = self.cols['publications']




    def get_publications(self, filters):
        pass

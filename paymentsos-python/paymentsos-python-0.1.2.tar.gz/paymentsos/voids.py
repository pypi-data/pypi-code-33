class Void(object):

    def __init__(self, client):
        self.client = client

    def create_void(self):
        raise NotImplementedError

    def retrieve_all_voids(self):
        raise NotImplementedError

    def retrieve_void(self):
        raise NotImplementedError

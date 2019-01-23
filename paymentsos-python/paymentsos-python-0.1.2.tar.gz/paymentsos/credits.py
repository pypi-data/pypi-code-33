class Credit(object):

    def __init__(self, client):
        self.client = client

    def create_credit(self):
        raise NotImplementedError

    def retrieve_all_credits(self):
        raise NotImplementedError

    def retrieve_credit(self):
        raise NotImplementedError

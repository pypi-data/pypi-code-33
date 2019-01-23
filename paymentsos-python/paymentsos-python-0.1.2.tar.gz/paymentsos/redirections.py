class Redirection(object):

    def __init__(self, client):
        self.client = client

    def retrieve_all_redirections(self):
        raise NotImplementedError

    def retrieve_redirection(self):
        raise NotImplementedError

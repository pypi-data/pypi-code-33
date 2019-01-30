import os


class Config:

    def __init__(self, data_dir=None):

        default_dir = os.path.dirname(os.path.realpath(__file__))

        if data_dir:
            self.data_dir = data_dir
        else:
            self.data_dir = default_dir

        self.db_dir = default_dir
        self.db_engine = 'sqlite:///' + self.db_dir + '/fec.db'

    def __str__(self):
        return "FEC Config Object"

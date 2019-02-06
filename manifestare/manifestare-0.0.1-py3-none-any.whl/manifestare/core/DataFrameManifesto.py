class DataFrameManifesto(object):

    def __init__(self):
        self.df = None

    def describeThat(self, df):
        self.df = df
        return self

    def end(self):
        self.df = None
        return
import pandas as pd

class PandasDataFrameTestBuilder(object):

    def buildEmptyDataFrame(self):
        return pd.DataFrame()

    def buildSimpleDataFrame(self):
        data = {
            'x': [0, 1],
            'y': [1, 0]
        }

        return pd.DataFrame(data)

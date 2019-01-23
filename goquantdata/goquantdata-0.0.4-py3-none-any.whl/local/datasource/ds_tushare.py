# cn market data only
#
from .datasource import DataSource

import tushare as ts

class TuShare(DataSource):
    def __init__(self):
        DataSource.__init__(self, name='TuShare')

    def get_stock_basics(self):
        df = ts.get_stock_basics()
        return df

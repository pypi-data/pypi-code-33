import pandas as pd
from datetime import datetime, date

import yahoo_finance
from yahoo_finance import Share

# from pandas_datareader import data as pdr
#
# import fix_yahoo_finance as yf
# yf.pdr_override() # <== that's all it takes :-)

import fix_yahoo_finance as yf
#data = yf.download("SPY", start="2017-01-01", end="2017-04-30")

from goquantdata.local.datasource.datasource import DataSource


class Yahoo(DataSource):
    def __init__(self, api_key=None):
        self.api_key = api_key

        # copy all function from original sdk
        for name in yahoo_finance.__dict__:  # iterate through every module's attributes
            val = yahoo_finance.__dict__[name]
            if callable(val):  # check if callable (normally functions)
                self.__dict__[name] = val
        DataSource.__init__(self, name='quandl')

    def connect(self):
        pass

    def get_daily(self, start_date, end_date, ids, market='us'):
        ret = pd.DataFrame()
        ids = list(set(ids))
        for i in range(len(ids)):
            symbol = ids[i]
            self.logger.info("processing symbol %s...%d/%d"%(symbol, i, len(ids)))
            try:
                cur = yf.download(symbol, start=start_date, end=end_date, progress=False)
                cur['symbol'] = symbol
                ret = pd.concat([ret, cur], axis=0)
            except ValueError:
                self.logger.warning("error when process symbol {}, skip".format(symbol))
        ret.rename(columns={'Adj Close': 'close',
                           'Low': 'low', 'High': 'high', 'Open':'open',
                           'Volume': 'volume'}, inplace=True)
        ret['date'] = ret.index
        ret = ret[["symbol", "date", "open", "high", "low", "close", "volume"]]
        return ret

if __name__ == "__main__":
    start_date = datetime.strptime("20170101", "%Y%m%d")
    end_date = datetime.strptime("20180101", "%Y%m%d")
    ids = ["AMD", "AAPL"]

    q = Yahoo()
    #print(q.get_symbol_list())

    df = q.get_daily(start_date, end_date, ids)

    # df = qd.get_daily(start_date, end_date, ['600848'], 'cn')
    print(df)




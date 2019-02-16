import pandas as pd
from datetime import datetime, date

import quandl
from io import BytesIO
from zipfile import ZipFile
from urllib.request import urlopen

from .datasource import DataSource


class Quandl(DataSource):
    def __init__(self, api_key):
        self.api_key = api_key

        # copy all function from original sdk
        for name in quandl.__dict__:  # iterate through every module's attributes
            val = quandl.__dict__[name]
            if callable(val):  # check if callable (normally functions)
                self.__dict__[name] = val
        DataSource.__init__(self, name='quandl')

    def connect(self):
        quandl.ApiConfig.api_key = self.api_key
        pass

    def get_daily(self, start_date, end_date, ids, market='us'):
        ret = pd.DataFrame()
        ids = list(set(ids))
        for i in range(len(ids)):
            symbol = ids[i]
            self.logger.info("processing symbol %s...%d/%d"%(symbol, i, len(ids)))
            try:
                if market == 'us':
                    cur = quandl.get('WIKI/{0}'.format(symbol), start_date=start_date, end_date=end_date, api_key=self.api_key)
                    cur['symbol'] = symbol
                    ret = pd.concat([ret, cur], axis=0)
                elif market == 'cn':
                    cur = quandl.get('DY4/{0}'.format(symbol), start_date=start_date, end_date=end_date, api_key=self.api_key)
                    cur['symbol'] = symbol
                    ret = pd.concat([ret, cur], axis=0)
                else:
                    self.logger.warning("market %s is not support now" % market)
            except quandl.NotFoundError:
                self.logger.warning("can't find symbol {}, skip".format(symbol))
            except ValueError:
                self.logger.warning("error when process symbol {}, skip".format(symbol))
        # rename
        ret.rename(columns={'Adj. Open': 'open', 'Adj. High': 'high',
                           'Adj. Low': 'low', 'Adj. Close': 'close',
                           'Adj. Volume': 'volume'}, inplace=True)
        ret['date'] = ret.index
        ret = ret[["symbol", "date", "open", "high", "low", "close", "volume"]]
        return ret

    def get_master_table(self):
        df = quandl.get_table('ZACKS/MT')
        return df

    def get_symbol_list(self):
        meta_url = quandl.ApiConfig.api_base + "/databases/EOD/metadata?api_key="+self.api_key

        resp = urlopen(meta_url)
        zipfile = ZipFile(BytesIO(resp.read()))
        file = zipfile.namelist()[0]

        ids = set()
        is_first = True
        for line in zipfile.open(file).readlines():
            if is_first:
                is_first = False
                continue
            ids.add(line.decode("utf-8").split(",")[0])
        ids = list(ids)
        ids.sort()
        ret = pd.DataFrame(index=range(len(ids)))
        ret['symbol'] = ids
        ret['date'] = datetime.combine(date.today(), datetime.min.time())
        return ret

if __name__ == "__main__":
    start_date = datetime.strptime("20170101", "%Y%m%d")
    end_date = datetime.strptime("20180101", "%Y%m%d")
    ids = ["AMD", "AAPL"]

    q = Quandl()
    print(q.get_symbol_list())

    #qd.get_daily(start_date, end_date, ids)

    # df = qd.get_daily(start_date, end_date, ['600848'], 'cn')
    # print(df)




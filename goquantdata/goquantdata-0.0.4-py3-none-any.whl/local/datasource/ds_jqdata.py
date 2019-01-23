import pandas as pd
from datetime import datetime, timedelta

import jqdatasdk

from .datasource import DataSource


class JQData(DataSource):
    RENAME_COL = {'1. open': 'open',
                  '2. high': 'high',
                  '3. low': 'low',
                  '4. close': 'close',
                  '5. volume': 'volume',
                  'date': 'date'}

    def __init__(self, api_key, api_username):
        self.api_key = api_key
        self.api_username = api_username
        # copy all function from original sdk
        for name in jqdatasdk.__dict__:  # iterate through every module's attributes
            val = jqdatasdk.__dict__[name]
            if callable(val):  # check if callable (normally functions)
                self.__dict__[name] = val
        DataSource.__init__(self, name=__name__)

    def connect(self):
        jqdatasdk.auth(self.api_username, self.api_key)

    def get_price(self):
        return None

    def local_build_dailydb(self, start_date, end_date, ids, db_dir):
        df = self.get_daily(start_date, end_date, ids)
        today = start_date
        while today < end_date:
            self.logger.info("date:%s" % today)
            if today not in df.index:
                today += timedelta(days=1)
                self.logger.info("skip.")
                continue
            cur_df = df.loc[today, :]
            filename = today.strftime("%Y%m%d") + ".csv"
            cur_df.to_csv(db_dir+"/"+filename, sep=',', index=False)
            today += timedelta(days=1)
        return df

    # def download_all_contract_data(self):
    #     df = pd.read_csv('futures_list_20181212.csv', index_col=0)
    #     for row in df.iterrows():
    #         contract = row[0]
    #         df_contract = get_price(contract, start_date=row[1]['start_date'], end_date=row[1]['end_date'])
    #         df_contract.to_csv('futures_data/' + contract[:-5] + '_20181212.csv')
    #     return None

    def get_daily(self, start_date, end_date, ids, market='cn'):
        if market != 'cn':
            self.logger("market type %s is not support"%market)
        if len(ids) == 0:
            return None
        pnl = jqdatasdk.get_price(security=ids,
                          start_date=start_date,
                          end_date=end_date,
                          frequency='daily',
                          fields=None,
                          skip_paused=False,
                          fq='pre',
                          count=None)
        ret = pd.DataFrame()
        for key in pnl.minor_axis:
            cur = pnl.minor_xs(key)
            cur['symbol'] = key
            cur['date'] = cur.index
            ret = pd.concat([ret, cur], axis=0)
        ret.sort_values(by='date', inplace=True)
        return ret


if __name__ == "__main__":
    start_date = datetime.strptime("20170101", "%Y%m%d")
    end_date = datetime.strptime("20180101", "%Y%m%d")
    ids = ["ZN9999.XSGE", "ZC9999.XZCE"]

    jqd = JQData()
    df = jqd.get_daily(start_date=start_date,
                       end_date=end_date,
                       ids=ids)

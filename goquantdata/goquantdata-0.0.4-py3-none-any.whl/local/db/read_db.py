from datetime import datetime
import os
import time

from datetime import timedelta
import pandas as pd

import goquantdata


def get_price(client,
              market,
              ids=list(),
              start_date=datetime.now(),
              end_date=datetime.now()):
    db_dir = client.db_dir + "/raw_" + market + "/"
    if not os.path.exists(db_dir):
        raise goquantdata.exceptions.InputError("can't find db dir %s, please run build bd first" % db_dir)
    df = pd.DataFrame()
    today = start_date
    while today < end_date:
        file_path = "%s/%s.csv" % (db_dir, today.strftime("%Y%m%d"))
        if os.path.exists(file_path):
            cur_df = pd.read_csv(file_path)
            cur_df = cur_df[cur_df['symbol'].isin(ids)]
            df = df.append(cur_df)
        today += timedelta(days=1)
    df.reset_index(drop=True, inplace=True)
    return df


def get_value(client,
              market,
              ids=list(),
              value_name="close",
              start_date=datetime.now(),
              end_date=datetime.now()):
    db_dir = client.db_dir + "/raw_" + market + "/"
    if not os.path.exists(db_dir):
        raise goquantdata.exceptions.InputError("can't find db dir %s, please run build bd first" % db_dir)
    df = pd.DataFrame()
    today = start_date
    while today < end_date:
        file_path = "%s/%s.csv" % (db_dir, today.strftime("%Y%m%d"))
        if os.path.exists(file_path):
            cur_df = pd.read_csv(file_path)
            cur_df = cur_df[cur_df['symbol'].isin(ids)]
            if value_name not in cur_df.columns:
                raise goquantdata.exceptions.InputError("can't find value %s file %s" % (value_name, file_path))
            df = df.append(cur_df[['symbol', 'date', value_name]])
        today += timedelta(days=1)
    df.set_index(['symbol', 'date'], inplace=True)
    df = df.unstack(level=0)
    df.columns = list(map("_".join, df.columns))
    df.reset_index(drop=False, inplace=True)
    return df


if __name__ == "__main__":
    from os.path import expanduser
    from goquantdata.local_client import LocalClient
    import goquantdata.local.private_config as cfg

    client = goquantdata.LocalClient(db_dir=expanduser("~") + '/data/localdb/',
                                     key_quandl=cfg.CONFIG_QUANDL['api_key'],
                                     jq_password=cfg.CONFIG_JQDATA['password'],
                                     jq_username=cfg.CONFIG_JQDATA['username'],
                                     key_alpha_vantage=cfg.CONFIG_ALPHA_VANTAGE['api_key'])
    start_time = time.time()

    ids_us = ["AAPL", "TD"]
    ids_cn = ["ZN9999.XSGE"]
    start_date = datetime(2019, 1, 11, 0, 0)
    end_date = datetime(2019, 1, 15, 0, 0)
    df = get_price(client=client,
                   market="us",
                   ids=ids_us,
                   start_date=start_date,
                   end_date=end_date)
    print(df)
    df = get_price(client=client,
                   market="cn",
                   ids=ids_cn,
                   start_date=start_date,
                   end_date=end_date)
    print(df)
    print("--- %s seconds ---" % (time.time() - start_time))

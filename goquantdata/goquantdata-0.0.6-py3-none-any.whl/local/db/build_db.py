import os
import time
from datetime import datetime, timedelta
import pandas as pd

from goquantdata.local.datasource.ds_quandl import Quandl
from goquantdata.local.datasource.ds_jqdata import JQData
from goquantdata.local.datasource.ds_yahoo import Yahoo
from goquantdata.local.datasource.ds_alpha_vantage import AlphaVantage
import goquantdata.util.util as util
from goquantdata.local.datasource.get_ids import get_wiki_sp500_ids, get_jq_xshg300_cn_ids, get_nasdaq_ids

logger = util.get_logger(name='build_db')

def _df2csv(df, start_date, end_date, out_dir):
    if not os.path.exists(out_dir):
        os.mkdir(out_dir)
    if df is None:
        return

    today = start_date
    while today < end_date:
        logger.info("date:%s" % today)
        if today not in df.index:
            today += timedelta(days=1)
            logger.info("skip.")
            continue
        cur_df = df.loc[today, :]
        filename = today.strftime("%Y%m%d") + ".csv"
        cur_df.to_csv(out_dir + "/" + filename, sep=',', index=False)
        today += timedelta(days=1)

def _local_build_alpha_vantage_stock(api_key, start_date, end_date, out_dir, ids=None):
    if ids is None:
        ids = get_nasdaq_ids()

    # try to download stock data
    av_ds = AlphaVantage(api_key)
    df = av_ds.get_daily(start_date, end_date, ids)
    _df2csv(df, start_date, end_date, out_dir)

    found_ids = set(df['symbol'].tolist())
    missed_ids = list(set(ids).difference(found_ids))
    return df, missed_ids
    return df

def _local_build_quandl_us_stock(key_quandl, start_date, end_date, out_dir, ids=None):
    # get stock universe
    if ids is None:
        ids = get_wiki_sp500_ids()
    # ids = get_nasdaq_ids()

    # try to download stock data
    quandl_ds = Quandl(key_quandl)
    df = quandl_ds.get_daily(start_date, end_date, ids)
    _df2csv(df, start_date, end_date, out_dir)

    found_ids = set(df['symbol'].tolist())
    missed_ids = list(set(ids).difference(found_ids))
    return df, missed_ids

def _local_build_yahoo_us_stock(start_date, end_date, out_dir, ids=None):
    # get stock universe
    if ids is None:
        ids = get_wiki_sp500_ids()
    # ids = get_nasdaq_ids()

    # try to download stock data
    yahoo_ds = Yahoo()
    df = yahoo_ds.get_daily(start_date, end_date, ids)
    _df2csv(df, start_date, end_date, out_dir)

    found_ids = set(df['symbol'].tolist())
    missed_ids = list(set(ids).difference(found_ids))
    return df, missed_ids

def _local_build_jqdata_cn_stock(jq_username, jq_password, start_date, end_date, out_dir, ids=None):
    if ids is None:
        ids = get_jq_xshg300_cn_ids(jq_username, jq_password)
    # ids_cmdty = get_cn_cmdty_ids()
    # ids += ids_cmdty
    jqd = JQData(api_key=jq_password, api_username=jq_username)
    df = jqd.get_daily(start_date=start_date,
                       end_date=end_date,
                       ids=ids)
    _df2csv(df, start_date, end_date, out_dir)

def _merge_us_cn_db(us_db_dir, cn_db_dir, out_dir, start_date, end_date):
    if not os.path.exists(out_dir):
        os.mkdir(out_dir)
    today = start_date
    while today < end_date:
        us_file_path = "%s/%s.csv" % (us_db_dir, today.strftime("%Y%m%d"))
        cn_file_path = "%s/%s.csv" % (cn_db_dir, today.strftime("%Y%m%d"))
        if os.path.exists(us_file_path) and os.path.exists(cn_file_path):
            out_file_path = "%s/%s.csv" % (out_dir, today.strftime("%Y%m%d"))
            us_df = pd.read_csv(us_file_path)
            us_df = us_df[["symbol", "date", "open", "high", "low", "close", "volume"]]
            us_df["market"] = "us"
            cn_df = pd.read_csv(cn_file_path)
            cn_df = cn_df[["symbol", "date", "open", "high", "low", "close", "volume"]]
            cn_df["market"] = "cn"
            df = pd.concat([us_df, cn_df], axis=0)
            df.to_csv(out_file_path, sep=',', index=False)
        today += timedelta(days=1)
    return


def build_db(client, start_date, end_date, ids_us=None, ids_cn=None):
    out_dir = client.db_dir
    if not os.path.exists(out_dir):
        os.makedirs(out_dir)
    raw_us_db = out_dir+"/raw_us/"
    raw_cn_db = out_dir+"/raw_cn/"
    # raw_db = out_dir+"/raw/"

    logger.info("download us market data")
    # _, missed_ids = _local_build_quandl_us_stock(client.key_quandl, start_date, end_date, raw_us_db, ids_us)
    # _, missed_ids = _local_build_alpha_vantage_stock(client.key_alpha_vantage, start_date, end_date, raw_us_db, ids_us)
    _, missed_ids = _local_build_yahoo_us_stock(start_date, end_date, raw_us_db, ids_us)



    logger.info("download cn market data")
    _local_build_jqdata_cn_stock(client.jq_username, client.jq_password, start_date, end_date, raw_cn_db, ids_cn)

    #logger.info("merge us and cn market data")
    #_merge_us_cn_db(raw_us_db, raw_cn_db, raw_db, start_date, end_date)
    logger.info("downloaded symbol: %d/%d, not downloaded symbol: %s" % (
    len(ids_us) - len(missed_ids), len(ids_us), missed_ids))


if __name__ == "__main__":
    start_time = time.time()
    start_date = datetime.strptime("20190102", "%Y%m%d")
    end_date = datetime.strptime("20190120", "%Y%m%d")

    from os.path import expanduser
    import goquantdata.local.private_config as cfg
    HOME_PATH = expanduser("~")
    DATA_DIR = HOME_PATH + '/data/local/'
    out_dir = DATA_DIR

    ids_us = ["TD", "AAPL", "AMD"]
    ids_cn = ["ZN9999.XSGE", "ZC9999.XZCE"]

    if not os.path.exists(out_dir):
        os.mkdir(out_dir)

    from goquantdata.local_client import LocalClient
    client = LocalClient(db_dir=expanduser("~") + '/data/localdb/',
                    key_quandl=cfg.CONFIG_QUANDL['api_key'],
                    jq_password=cfg.CONFIG_JQDATA['password'],
                    jq_username=cfg.CONFIG_JQDATA['username'],
                    key_alpha_vantage=cfg.CONFIG_ALPHA_VANTAGE['api_key'])

    build_db(client, start_date, end_date, ids_us, ids_cn)
    logger.info("--- %s seconds ---" % (time.time() - start_time))


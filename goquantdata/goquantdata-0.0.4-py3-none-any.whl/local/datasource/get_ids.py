import pandas as pd
import requests
import io

from goquantdata.local.datasource.ds_quandl import Quandl
from goquantdata.local.datasource.ds_jqdata import JQData

def get_wiki_sp500_ids():
    symbols_table = pd.read_html("https://en.wikipedia.org/wiki/List_of_S%26P_500_companies",
                                 header=0)[0]
    symbols = list(symbols_table.loc[:, "Symbol"])
    return symbols

def get_nasdaq_ids():
    url_NASDAQ = "http://www.nasdaq.com/screening/companies-by-industry.aspx?exchange=NASDAQ&render=download"
    url_NYSE = "http://www.nasdaq.com/screening/companies-by-industry.aspx?exchange=NYSE&render=download"
    url_asxl = "http://www.asx.com.au/asx/research/ASXListedCompanies.csv"

    symbols = []

    urlData = requests.get(url_NASDAQ).content
    rawData = pd.read_csv(io.StringIO(urlData.decode('utf-8')))
    symbols += rawData['Symbol'].tolist()

    # urlData = requests.get(url_NYSE).content
    # rawData = pd.read_csv(io.StringIO(urlData.decode('utf-8')))
    # symbols += rawData['Symbol'].tolist()

    #rawData = pd.read_csv(url_asxl, header=1)
    #symbols += rawData['Symbol'].tolist()
    return symbols


def get_quandl_us_ids(api_key):
    quandl_ds = Quandl(api_key)
    df_ids = quandl_ds.get_symbol_list()
    df_ids.set_index("date", inplace=True, drop=False)
    df_ids["market"] = "us"

    cur_df = df_ids.loc[:, ["symbol", "market"]]
    ids = cur_df['symbol'].tolist()
    return ids

def get_jq_xshg300_cn_ids(username, password):
    ds_jqdata = JQData(api_key=password, api_username=username)
    ids = ds_jqdata.get_index_stocks(index_symbol='000300.XSHG')
    return ids

def get_cn_cmdty_ids():
    ids = ["SC","SP","CU","AL","PB","ZN","SN","NI","RU","RB","BU","HC","AG","AU","WR","FU","EG","C","CS","A","V","L",
           "PP","B","M","Y","P","J","JM","I","JD","BB","FB","AP","ZC","RM","OI","SR","RI","JR","LR","PM","RS","SM",
           "SF","FG","WH","MA","CF","CY","TA","IC","IF","IH"]
    return ids

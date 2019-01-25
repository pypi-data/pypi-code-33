import json
import pandas as pd
import requests


url = "https://finfoapi-hn.vndirect.com.vn/stocks/adPrice"


class VndPrice:
    def __init__(self):
        pass

    def getHistAd(self, ticker=None, fromDate=None, toDate=None):
        """
        acept argument:
        ticker: stock ticker
        fromDate: acept format yyyy-mm-dd
        toDate: acept format yyyy-mm-dd
        """
        queryString = {"symbols": ticker, "fromDate": fromDate, "toDate": toDate}
        data = requests.get(url, params=queryString).text
        df = pd.DataFrame(json.loads(data)["data"])
        return df

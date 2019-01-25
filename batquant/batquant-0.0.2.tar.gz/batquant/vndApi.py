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
        queryString = {"symbol": ticker, "fromDate": fromDate, "toDate": toDate}
        data = requests.get(url, params=queryString).text
        return data

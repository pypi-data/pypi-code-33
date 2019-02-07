import http.client
import pandas as pd
from .config import Config


def get(dataset, **kwargs):
    """
    Return DataFrame of requested DecisionForest dataset.
    Args:
        dataset (str): Dataset codes are available on DecisionForest.com, example: dataset='SMD'
        ** date (str): Date, example: date='2018-12-28'
        ** start, end (str): Date filters, example: start='2018-12-28', end='2018-12-30'
        ** symbol (str): Symbol codes are available on DecisionForest.com on the product page , example: symbol='AAPL'
    """

    conn = http.client.HTTPSConnection(Config.DOMAIN)
    u = f"/api/{dataset}/?key={Config.KEY}"

    for key, value in kwargs.items():
        u = f'{u}&{key}={value}'

    conn.request("GET", u)
    res = conn.getresponse()
    data = res.read()
    data = data.decode("utf-8")
    data = eval(data)
    if dataset == 'SMD':
        d = {}
        for i in range(len(data)):
            d[i] = {}
            d[i]['date'] = data[i]['date']
            d[i]['symbol'] = data[i]['symbol']
            d[i]['sentiment'] = data[i]['sentiment']
            d[i]['probability'] = data[i]['probability']
            d[i]['ratio'] = data[i]['ratio']

        df = pd.DataFrame.from_dict(d, orient='index')
    else:
        df = pd.DataFrame()

    return df

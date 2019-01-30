import datetime
import pandas as pd
from WindPy import w

w.start()

__all__ = ['wsd', 'wss']

def wsd(codes, fields, first_date, last_date, options=None):
    if isinstance(codes, str):
        codes = codes.split(',')
    if isinstance(fields, str):
        fields = fields.split(',')

    dfs = {}

    if len(fields) == 1:
        ret = w.wsd(codes, fields[0], first_date, last_date, options)
        for i in range(len(codes)):
            dfs[codes[i]] = pd.DataFrame({ fields[0]: ret.Data[i] }, index=ret.Times)
    else:
        for c in codes:
            ret = w.wsd(c, fields, first_date, last_date, options)
            data = {fields[i]: ret.Data[i] for i in range(len(fields))}
            dfs[c] = pd.DataFrame(data, index=ret.Times)

    result = pd.concat([dfs[c] for c in codes], axis=1, keys=codes, names=['codes', 'fields'])
    result.index.name = 'date'
    return result


def wss(codes, fields, date=None):
    if isinstance(codes, str):
        codes = codes.split(',')
    if isinstance(fields, str):
        fields = fields.split(',')
    if isinstance(date, datetime.date):
        date = date.strftime('%Y%m%d')
    ret = w.wss(codes, fields, f"tradeDate={date};priceAdj=U;cycle=D" if date is not None else None)

    data = {fields[i]: ret.Data[i] for i in range(len(fields))}
    return pd.DataFrame(data, index=codes)

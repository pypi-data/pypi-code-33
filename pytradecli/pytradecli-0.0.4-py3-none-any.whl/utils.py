import pandas as pd


class SymbolNotFoundError(Exception):
    def __init__(self, message):
        self._message = message

    def __str__(self):
        return self._message


class DateTimeError(Exception): 
    def __init__(self, message):
        self._message = message

    def __str__(self):
        return self._message


def date_to_string(dt):
    try:
        return str(dt.date())
    except AttributeError:
        return None


def datetime_to_string(dt):
    try:
        return f"{dt.isoformat()}Z"
    except AttributeError:
        return None


def get_date_string(data_types, date=None, start=None, end=None):
    if all((date, start)):
        raise DateTimeError("dateとstartは同時に指定できません")
    try:
        date_, start_, end_ = (
            pd.to_datetime(date),
            pd.to_datetime(start),
            pd.to_datetime(end),
        )
    except ValueError:
        raise DateTimeError("日付のフォーマットが正しくありません")
    if all((start_, end_)) and start_ >= end_:
        raise DateTimeError("start<endとしてください")
    func = {"bar": date_to_string, "tick": datetime_to_string}
    return {
        "date": func[data_types](date_),
        "start": func[data_types](start_),
        "end": func[data_types](end_),
    }


def get_endpoint_by_symbol(
    symbol, data_types="default", date=None, start=None, end=None
):
    # 4桁の数字の場合は日本株の4本値のエンドポイントを返す
    four_digit_int = isinstance(symbol, int) and len(str(symbol)) == 4
    four_digit_str = isinstance(symbol, str) and symbol.isdigit()
    if any((four_digit_int, four_digit_str)):
        endpoint, data_types = "stock_ohlcv_jp", "bar"
        return endpoint, data_types

    # 先物(N225FUTではじまる)の場合は4本値のエンドポイントを返す
    if symbol.startswith("N225FUT"):
        data_types = "bar"
        endpoints = {
            "N225FUT": "n225fut_ohlcv",
            "N225FUTD": "n225fut_ohlcv_day",
            "N225FUTN": "n225fut_ohlcv_night",
        }
        endpoint = endpoints[symbol]
        return endpoint, data_types

    # 先物オプション(N225FOP)の場合は日付の指定がなければ最新のエンドポイントを返す
    if symbol == "N225FOP":
        data_types = "tick"
        if any((date, start)):
            endpoint = "n225fop"
        else:
            endpoint = "n225fop_latest"
        return endpoint, data_types

    raise SymbolNotFoundError("指定したSymbolが見つかりません")


def format_fields(data, kind):
    if isinstance(data, str):
        data = set([data])
    elif isinstance(data, list):
        data = set(data)
    else:
        return None
    
    if kind == "include":
        data.update(["date"])
    elif kind == "exclude" and "date" in data:
        data.remove("date")
    return list(data)
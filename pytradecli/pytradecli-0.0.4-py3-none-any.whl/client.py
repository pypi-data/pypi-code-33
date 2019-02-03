from urllib.parse import urljoin
import pandas as pd

from . import api, api_config, utils


class Client:
    """
    APIクライアント

    Parameters
    ----------
    token: str
        Authorization Token
    """

    base_endpoint = "api/v1/"
    columns_order = pd.Index(
        [
            "date",
            "symbol",
            "open",
            "high",
            "low",
            "close",
            "adj_close",
            "volume",
            "maturity",
            "strike",
            "fop_type",
            "bid",
            "bid_qty",
            "ask",
            "ask_qty",
            "mid",
        ]
    )

    def __init__(self, token="", api_host=""):
        if token:
            self.token = token
        else:
            self.token = api_config.load_token()
        if api_host:
            self.api_host = api_host
        else:
            self.api_host = api_config.load_api_host()

    def save_token(self, token=""):
        if token:
            api_config.save_token(token)
        else:
            api_config.save_token(self.token)
    
    def save_api_host(self, api_host=""):
        if api_host:
            api_config.save_api_host(api_host)
        else:
            api_config.save_api_host(self.api_host)

    def get(
        self,
        symbol,
        data_types="default",
        date=None,
        start=None,
        end=None,
        maturity=None,
        strike=None,
        fop_type=None,
        include=None,
        exclude=None,
    ):
        """
        APIから4本値またはティックデータを取得

        Parameters
        ----------
            symbol: int, str
                4桁の整数: 日本株の4本値
                N225FUT: 日経225先物の4本値(日通し)
                N225FUTD: 日経225先物の4本値(日中)
                N225FUTN: 日経225先物の4本値(夜間)
                N225FOP: 日経225ミニ及びオプションの呼び値(3限月)
            data_types: str
                default: 自動判別
                bar: 4本値
                tick: ティック(呼び値)
            date: str
                取得日時
            start: str
                取得開始日時
            end: str
                取得終了日時
            include: list
                取得するフィールドを選択
            exclude: list
                除外するフィールドを選択
        """

        endpoint, data_types = utils.get_endpoint_by_symbol(
            symbol, data_types, date, start, end
        )
        date_params = utils.get_date_string(data_types, date, start, end)
        uri = urljoin(urljoin(f"http://{self.api_host}", self.base_endpoint), endpoint)

        include = utils.format_fields(include, "include")
        exclude = utils.format_fields(exclude, "exclude")

        params = {
            "symbol": symbol,
            "maturity": maturity,
            "strike": strike,
            "fop_type": fop_type,
            "include": include,
            "exclude": exclude,
        }
        params.update(date_params)
        if data_types == "tick":
            params["symbol"] = None
        self.uri = uri
        self.params = params
        self.api = api.API(token=self.token)
        self.dicts = api.API(token=self.token).get_json(self.uri, self.params)

        if self.dicts:
            df = pd.DataFrame(self.dicts)
            # columns_order順に並び替え
            df = df[[c for c in self.columns_order if c in df.columns]]
            df["date"] = pd.to_datetime(df["date"])
            df.set_index("date", inplace=True)
            self.df = df
        else:
            self.df = None
        
        return self.df

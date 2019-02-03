from . import client


def get(symbol, token="", api_host="", *args, **kwargs):
    """
    APIから4本値またはティックデータを取得

    Parameters
    ----------
        token: str
            Authorization Token
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
    cli = client.Client(token=token)
    cli.get(symbol, *args, **kwargs)
    return cli.df

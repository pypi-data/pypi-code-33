import requests


class ApiError(Exception):
    def __init__(self, message):
        self._message = message

    def __str__(self):
        return self._message


class API:
    """
    APIサーバからデータをリクエスト

    Parameters
    ----------
    token: str
        Authorization Token
    """

    MAX_PAGE_COUNT = 100

    def __init__(self, token=""):
        self.token = token
        self.headers = {
            "Authorization": f"Token {self.token}",
            "Content-Type": "application/json; charset=utf-8",
        }

    def get_response(self, uri, params):
        """
        requests.getの結果をインスタンスに追加

        Parameters
        ----------
        uri: str
            APIのエンドポイント
        params: dict
            APIのパラメータ        
  
        Returns
        -------
        respons: requests.models.Response
            requests.getの結果
        """
        if not self.token:
            raise ApiError("API Tokenが設定されていません")

        res = requests.get(uri, params=params, headers=self.headers)
        res.raise_for_status()

        return res

    def get_json(self, uri, params):
        results = []
        for i in range(self.MAX_PAGE_COUNT):
            res = self.get_response(uri, params)
            json_data = res.json()
            results += json_data["results"]
            uri = json_data["next"]
            if uri:
                params = {}
            else:
                break

        return results

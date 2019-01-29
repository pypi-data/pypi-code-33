# -*- coding: utf-8 -*-

try:
    from urllib.parse import urljoin
except ImportError:
    from urlparse import urljoin

from tpspy.auth.authutil import AuthUtil


class ResponseCode:
    CODE_SUCCESS = 10000


class ClientBase(object):
    user_api = "API"

    def __init__(self, sys_id=None, sys_secret=None, tps_base_url=None):
        self.tps_base_url = tps_base_url or "https://tencent.qq.com/"
        self.sys_id = sys_id
        self.sys_secret = sys_secret
        self.auth = AuthUtil()
        self.auth.set_secret(self.sys_secret)

    def set_tps_base_url(self, tps_base_url):
        self.tps_base_url = tps_base_url

    @property
    def token(self):
        return self.auth.gen_token(user_id="API")

    @property
    def auth_headers(self):
        return {
            "SYS-ID": self.sys_id,
            "TOKEN": self.token,
        }

    @property
    def post_headers(self):
        headers = {
            "Content-Type": "application/json"
        }
        headers.update(self.auth_headers)
        return headers

    @property
    def get_headers(self):
        headers = {
            "Content-Type": "application/json"
        }
        headers.update(self.auth_headers)
        return headers

    @staticmethod
    def resp_get_json(resp):
        try:
            return resp.json()
        except:
            raise Exception("resp is not json: ", resp.status_code, resp.text)


if __name__ == "__main__":
    pass

# encoding=utf-8
# date: 2018/7/17
__Author__ = "Masako"

import requests


class Spider(object):
    def __init__(self):
        self.host = ""
        self.origin_url = ""
        self.detail_url = ""
        self.list_url = ""
        self.proxies = None
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.77 Safari/537.36",
        }

    @staticmethod
    def request_get(url, parse_func, headers, proxies=None, **request_params):
        result = {}
        params = request_params.get('params')
        timeout = request_params.get('timeout', 5)
        charset = request_params.get('charset', 'utf-8')
        try:
            r = requests.get(url, params=params, headers=headers, proxies=proxies, timeout=timeout)
        except Exception as e:
            result['code'] = 1
            result['msg'] = str(e)
            return result

        try:
            content = r.content.decode(charset)
            data = parse_func(content)
        except Exception as e:
            result['code'] = 2
            result['msg'] = str(e)
            return result

        result['code'] = 0
        result['data'] = data
        return result

    @staticmethod
    def request_post(url, parse_func, headers, proxies=None, **request_params):
        result = {}
        # , params, data=None, json=None , timeout=5
        params = request_params.get('params')
        data = request_params.get('data')
        jsn = request_params.get('json')
        timeout = request_params.get('timeout', 5)
        charset = request_params.get('charset', 'utf-8')
        try:
            r = requests.post(url, headers=headers, params=params, data=data, json=jsn, proxies=proxies,
                              timeout=timeout)
        except Exception as e:
            result['code'] = 1
            result['msg'] = str(e)
            return result

        # print(r.text)
        try:
            content = r.content.decode(charset)
            data = parse_func(content)
        except Exception as e:
            result['code'] = 2
            result['msg'] = str(e)
            return result

        result['code'] = 0
        result['data'] = data
        return result

    def get_list(self, method='get', **kwargs):
        if method == 'get':
            return self.request_get(self.list_url, self.parse_list, self.headers, self.proxies, **kwargs)
        elif method == 'post':
            return self.request_post(self.list_url, self.parse_list, self.headers, self.proxies, **kwargs)
        else:
            print('method not support')

    def get_detail(self, method='get', **kwargs):
        if method == 'get':
            return self.request_get(self.detail_url, self.parse_detail, self.headers, self.proxies, **kwargs)
        elif method == 'post':
            return self.request_post(self.detail_url, self.parse_detail, self.headers, self.proxies, **kwargs)
        else:
            print('method not support')

    def parse_list(self, content):
        pass

    def parse_detail(self, content):
        pass


if __name__ == "__main__":
    spider = Spider()
    spider.origin = "https://www.marathon.tokyo/2018/result/index.php"

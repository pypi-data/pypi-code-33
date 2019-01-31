# -*- coding: utf-8 -*-
# import httplib2
import os
import json
import urllib

import httplib2

from util.decorators import *
from pathlib import Path
import requests


DEFAULT_CACHE_DIR = 'D:\\dev\\_workspace\\.cache'
if Path('D:\\dev').is_dir():
    os.makedirs(DEFAULT_CACHE_DIR, exist_ok=True)
    http = httplib2.Http(DEFAULT_CACHE_DIR)
else:
    http = httplib2.Http()


@retry(Exception, retry=10, default_result={})
def request(url, method='GET', params=None, headers={}, return_json=False, ):
    body = None
    if 'GET' == method and params is not None:
        url = url.format(**params)
    else:
        if params is not None:
            body = urllib.parse.urlencode(params)

    print('loading ', url)
    _, content = http.request(url, method, body, headers=headers)

    if return_json:
        return json.loads(content) if content else {}
    else:
        return content


def shorten_url(url):
    """
    生成短网址
    """
    response = requests.post(url='https://dwz.cn/admin/v2/create', data=json.dumps({'url': url}),
                             headers={'Content-Type': 'application/json', 'Token': '861201aae84688ca9dfd7bc818384ef7'})
    return json.loads(response.text)['ShortUrl']

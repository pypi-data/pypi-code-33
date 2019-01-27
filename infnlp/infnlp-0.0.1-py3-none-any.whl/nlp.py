
import json
import requests

ROOT = 'http://nlpapi.infuture.tech'


def tokenize(content):
    ret = requests.post(ROOT + '/hanlp/tokenize', json={
        'content': content
    }, timeout=30)
    ret = json.loads(ret.text)
    if isinstance(ret, dict) and 'success' in ret and ret['success']:
        return ret['result']
    else:
        if isinstance(ret, dict) and 'error' in ret:
            raise RuntimeError(ret['error'])
        else:
            raise RuntimeError('Unkown Error')


if __name__ == '__main__':
    ret = tokenize('我爱北京天安门')
    print(ret)

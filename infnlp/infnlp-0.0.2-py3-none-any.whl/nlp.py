
import os
import json
import requests

ROOT = 'http://nlpapi.infuture.tech'
if 'INFNLP_ROOT' in os.environ:
    ROOT = os.environ['INFNLP_ROOT']
TOKEN = ''
if 'INFNLP_TOKEN' in os.environ:
    TOKEN = os.environ['INFNLP_TOKEN']
headers = {'infnlp_token': TOKEN}


def return_result(ret):
    ret = json.loads(ret.text)
    if isinstance(ret, dict) and 'success' in ret and ret['success']:
        return ret['result']
    else:
        if isinstance(ret, dict) and 'error' in ret:
            raise RuntimeError(ret['error'])
        else:
            raise RuntimeError('Unkown Error')


def tokenize(content, no_pos=True, engine='StandardTokenizer'):
    ret = requests.post(ROOT + '/hanlp/tokenize', headers=headers, json={
        'content': content,
        'no_pos': no_pos,
        'engine': engine
    }, timeout=30)
    return return_result(ret)


def pos(content, engine='StandardTokenizer'):
    ret = requests.post(ROOT + '/hanlp/pos', headers=headers, json={
        'content': content,
        'engine': engine
    }, timeout=30)
    return return_result(ret)


def extract_keywords(content, number=5):
    ret = requests.post(ROOT + '/hanlp/extract_keywords', headers=headers, json={
        'content': content,
        'number': number
    }, timeout=30)
    return return_result(ret)


def extract_summary(content, number=5):
    ret = requests.post(ROOT + '/hanlp/extract_summary', headers=headers, json={
        'content': content,
        'number': number
    }, timeout=30)
    return return_result(ret)


def extract_phrase(content, number=5):
    ret = requests.post(ROOT + '/hanlp/extract_phrase', headers=headers, json={
        'content': content,
        'number': number
    }, timeout=30)
    return return_result(ret)


def add(word):
    ret = requests.post(ROOT + '/hanlp/add', headers=headers, json={
        'word': word
    }, timeout=30)
    return return_result(ret)


def insert(word, info):
    ret = requests.post(ROOT + '/hanlp/insert', headers=headers, json={
        'word': word,
        'info': info
    }, timeout=30)
    return return_result(ret)


def parse(content):
    ret = requests.post(ROOT + '/hanlp/parse', headers=headers, json={
        'content': content
    }, timeout=30)
    return return_result(ret)


def pinyin(content, method):
    ret = requests.post(ROOT + '/hanlp/pinyin', headers=headers, json={
        'content': content,
        'method': method
    }, timeout=30)
    return return_result(ret)


def s2t(content):
    ret = requests.post(ROOT + '/hanlp/s2t', headers=headers, json={
        'content': content
    }, timeout=30)
    return return_result(ret)


def t2s(content):
    ret = requests.post(ROOT + '/hanlp/t2s', headers=headers, json={
        'content': content
    }, timeout=30)
    return return_result(ret)


if __name__ == '__main__':
    ret = tokenize('我爱北京天安门')
    print(ret)

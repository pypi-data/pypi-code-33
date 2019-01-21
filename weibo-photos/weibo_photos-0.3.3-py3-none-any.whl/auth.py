import requests
import pickle
import base64
import binascii
import time
import random
import math
import json
import rsa
import re
from urllib.parse import quote, unquote

def make_rsa_passwd(pubkey, nonce, servertime, password):
    rsaPublickey = int(pubkey, 16)
    key = rsa.PublicKey(rsaPublickey, 65537) #创建公钥
    message = str(servertime) + '\t' + str(nonce) + '\n' + str(password) #拼接明文js加密文件中得到
    passwd = rsa.encrypt(message.encode(), key) #加密
    passwd = binascii.b2a_hex(passwd) #将加密信息转换为16进制。
    return passwd

def login(session, name, password):
    name_url_encode = quote(name, 'utf-8')
    name_base64_encode = base64.b64encode(bytes(name_url_encode, 'utf-8'))
    pre_time_stamp = str(int(time.time() * 1000))

    prelogin_url = 'https://login.sina.com.cn/sso/prelogin.php'
    payloads = {
        'entry': 'weibo',
        'callback': 'sinaSSOController.preloginCallBack',
        'su': name_base64_encode,
        'rsakt': 'mod',
        'checkpin': '1',
        'client': 'ssologin.js(v1.4.19)',
        '_': pre_time_stamp
    }
    r = session.get(prelogin_url, params=payloads)
    r.raise_for_status()
    html = r.text
    html = html.split('(', 1)[1]
    html = html.rsplit(')', 1)[0]
    res_dict = json.loads(html)
    nonce = res_dict['nonce']
    rsakv = res_dict['rsakv']
    pubkey = res_dict['pubkey']

    time_stamp = str(int(time.time()))
    login_url = 'https://login.sina.com.cn/sso/login.php'
    params = {
        'client': 'ssologin.js(v1.4.19)'
    }
    data = {
        'entry': 'weibo',
        'gateway': '1',
        'from': '', 
        'savestate': '7',
        'qrcode_flag': 'false',
        'useticket': '1',
        'pagerefer': 'https://passport.weibo.com/visitor/visitor?entry=miniblog&a=enter&url=https%3A%2F%2Fweibo.com%2F&domain=.weibo.com&ua=php-sso_sdk_client-0.6.28&_rand=1547702005.9422',
        'vsnf': '1',
        'su': name_base64_encode,
        'service': 'miniblog',
        'servertime': time_stamp,
        'nonce': nonce,
        'pwencode': 'rsa2',
        'rsakv': rsakv,
        'sp': make_rsa_passwd(pubkey, nonce, time_stamp, password),
        'sr': '1680*1050',
        'encoding': 'UTF-8',
        'prelt': '183',
        'url': 'https://weibo.com/ajaxlogin.php?framelogin=1&callback=parent.sinaSSOController.feedBackUrlCallBack',
        'returntype': 'META'
    }
    r = session.post(login_url, params=params, data=data)
    r.raise_for_status()
    r.encoding = 'gbk'
    html = r.text
    retcode_pattern = 'retcode%3D(.*?)&'
    url_pattern = 'r=(https.*?)&'
    retcode = re.findall(retcode_pattern, html)[1]
    if retcode != '0':
        raise Exception('Login error!')
    url = re.findall(url_pattern, html)[1]
    url = unquote(url, 'utf-8')
    r = session.get(url)
    r.raise_for_status()
    with open('cookies', 'wb') as f:
        pickle.dump(session.cookies, f)
    print('登录成功！')
    
if __name__ == "__main__":
    s = requests.Session()
    s.headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/69.0.3497.100 Safari/537.36',
        'Referer': 'https://webo.com/'
    }
    s.verify = False
    login(s, '', '')
    r = s.get('https://weibo.com/')
    print(r.url)
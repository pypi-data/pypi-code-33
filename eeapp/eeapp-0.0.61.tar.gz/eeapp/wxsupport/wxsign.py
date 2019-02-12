
from django.conf import settings
import hashlib
import datetime
import requests

wx_merch_id = settings.WX_MERCHID
wx_merch_key = settings.WX_MERCHKEY
wx_app_id = settings.WX_APPID
wx_app_secret = settings.WX_APPSECRET


notify_url = 'http://new.doncheng.cn/web/api/wx/paynotice'

# 微信配置基础数据
WPC = {
    'APPID': wx_app_id,
    'APPSECRET': wx_app_secret,
    'MCHID': wx_merch_id,
    'KEY': wx_merch_key,
    'GOODDESC': '商户号中的公司简称或全称-无要求的商品名字',
    'NOTIFY_URL': 'http://new.doncheng.cn/app/auth',
}

# 获取MD5
def MD5(str):
    md5 = hashlib.md5()
    md5.update(str.encode('utf-8'))
    return md5.hexdigest()

#生成随机字符串
def getNonceStr():
    import random
    data="123456789zxcvbnmasdfghjklqwertyuiopZXCVBNMASDFGHJKLQWERTYUIOP"
    nonce_str  = ''.join(random.sample(data , 30))
    return nonce_str

#生成商品订单号
def getWxPayOrdrID():
    date = datetime.datetime.now()
    #根据当前系统时间来生成商品订单号。时间精确到微秒
    payOrdrID=date.strftime("%Y%m%d%H%M%S%f")

    return payOrdrID


class WXSign(object):
    @classmethod
    def getSign(cls, kwargs):
        # 计算签名
        keys, paras = sorted(kwargs), []
        paras = ['{}={}'.format(key, kwargs[key]) for key in keys if key != 'appkey']  # and kwargs[key] != '']
        stringA = '&'.join(paras)

        stringSignTemp = stringA + '&key=' + WPC['KEY']
        sign = MD5(stringSignTemp).upper()
        return sign

    @classmethod
    def getxml(cls, kwargs):
        kwargs['sign'] = WXSign.getSign(kwargs)

        # 生成xml
        xml = ''
        for key, value in kwargs.items():
            xml += '<{0}>{1}</{0}>'.format(key, value)
        xml = '<xml>{0}</xml>'.format(xml)
        # print(xml)
        return xml


    @classmethod
    def genData(cls,openid,spbill_create_ip,body,price):
        price = int(price * 100)
        nonce_str = getNonceStr()
        # order_no = wx_merch_id + str(getWxPayOrdrID())
        order_no = str(getWxPayOrdrID())

        UnifieOrderRequest = {
            'appid': wx_app_id,  # 公众账号ID
            'body': body,  # 商品描述
            'mch_id': wx_merch_id,  # 商户号:深圳市泽慧文化传播有限公司
            'nonce_str': nonce_str,  # 随机字符串
            'notify_url': notify_url,  # 微信支付结果异步通知地址
            'openid': openid,  # trade_type为JSAPI时，openid为必填参数！此参数为微信用户在商户对应appid下的唯一标识, 统一支付接口中，缺少必填参数openid！
            'out_trade_no': order_no,  # 商户订单号
            'spbill_create_ip': spbill_create_ip,  # 终端IP
            'total_fee': price,  # 标价金额
            'trade_type': 'JSAPI',  # 交易类型
        }
        return WXSign.getxml(UnifieOrderRequest),order_no
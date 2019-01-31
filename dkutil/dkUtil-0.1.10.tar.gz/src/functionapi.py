# coding:utf-8
import sys
if sys.version > '3':
    PY3 = True
else:
    PY3 = False
if PY3:
    from configparser import ConfigParser
else:
    from ConfigParser import ConfigParser
from urllib import parse
from urllib import request
import hashlib
import string
from decipheringapi import decipheringapi
class functionapi(object):
    def __init__(self,otsapihost):
        self.otsapihost = otsapihost
    @staticmethod
    def http_post_req(requrl,post_data):
        '''
        发送post请求
        :param requrl:
        :param post_data:
        :return:
        '''
        post_data_urlencode = parse.urlencode(post_data,"utf-8").encode(encoding='UTF8')
        header = {}
        header["Content-Type"] = "application/x-www-form-urlencoded;charset=UTF-8"
        req = request.Request(url=requrl, data=post_data_urlencode,headers=header)
        res_data = request.urlopen(req)
        res = res_data.read()
        return str(res, encoding = "utf-8")
    @staticmethod
    def http_get_rep(requrl,getparam):
        '''
        http get 请求
        :param requrl:
        :return:
        '''
        param = []
        for k,v in getparam.items():
            param.append("%s=%s" %(k,v))
        requrl = "%s?%s" %(requrl,"&".join(param))
        s = parse.quote(requrl, safe=string.printable)
        req = request.Request(url=s)
        res_data = request.urlopen(req)
        res = res_data.read()
        return str(res, encoding="utf-8")
    @staticmethod
    def MD5DecodeStr(str,upper=True):
        '''
        字符串MD5解密
        :param str:需要加密的字符串
        :upper: 是否输出大写，默认大写
        :return:MD5解密后的密文
        '''
        filemd5 = None
        try:
            m2 = hashlib.md5()
            m2.update(str.encode("utf8"))
            filemd5 = m2.hexdigest()
        except:
            print(sys.exc_info())
        if upper:
            return filemd5.upper()
        return filemd5

    @staticmethod
    def decipheringPhone(host, phonelist, pre_page_count=40):
        '''
        批量解密MD5手机号
        :param host:接口api地址
        :param phonelist:解密手机号，都好分割
        :param pre_page_count:每次解密数，下于接口本身支持最大条数
        :return:解密后的手机号数组
        '''
        phonemd5 = phonelist.split(",")
        phonelist = []
        desc = decipheringapi(host)
        # 数组分页，每段40
        currypage = 0
        total_page_count, div = divmod(phonemd5.__len__(), pre_page_count)
        if div:
            # 如果 div 有值 总页数 +1
            total_page_count += 1
        while total_page_count > 0:
            pagedata = phonemd5[currypage * pre_page_count:(currypage + 1) * pre_page_count]  # 前闭后开[)区间
            phonelist += desc.md5decipheringByOts(pagedata)
            currypage += 1
            total_page_count -= 1
        return phonelist
    @staticmethod
    def confInit(confile):
        '''
        配置文件初始化
        :param confile:
        :return:
        '''
        config = ConfigParser()
        config.read(confile, encoding="utf-8")
        return config
    @staticmethod
    def getmqConfig(conf):
        '''
        获取消息队列配置参数
        :param conf: ConfigParser 实例
        :return: 配置参数
        '''
        section = "rabbimq"
        host = conf.get(section, "host")
        port = conf.get(section, "port")
        username = conf.get(section, "username")
        password = conf.get(section, "password")
        virtualhost = conf.get(section, "virtualhost")
        return host, username, password, virtualhost, port
    @staticmethod
    def getOtsConfig(conf):
        '''
        获取表格存储需要的参数
        :param conf:ConfigParser 实例
        :return:
        '''
        section = "tablestore"
        endPoint = conf.get(section, "endPoint")
        accessId = conf.get(section,"accessId")
        accessKey = conf.get(section, "accessKey")
        instanceName = conf.get(section, "instanceName")
        return endPoint,accessId,accessKey,instanceName

    @staticmethod
    def getConfigureChannelId(conf):
        '''
        得到通道的通道号
        :param conf:
        :return:
        '''
        return conf.get("channel", "channel_1")
    @staticmethod
    def getConfig(conf,section,key):
        '''
        获取指定section下面的key
        :param conf:
        :param section:
        :param key:
        :return:
        '''
        return conf.get(section,key)
# -*- coding:utf-8 -*-
__authon__ = "cfn@leapy.cn"

import requests
from wxbot import wxmessage,wxconf,wxmail
import time
import re
import sys
import random
from wxbotdb import dbconnect
import os

class parse(wxmessage.message):
    def __init__(self):
        wxmessage.message.__init__(self)
        self.session = requests.session()
        self.mydb = dbconnect.db()
        self.image = ""
        self.uuid = ''
        self.deviceId = ""
        self.loginInfo = ""
        self.cookie = ""
        self.pass_ticket = ""
        self.lang = ""
        self.qrCodeType = wxconf.WXConf().baseconf['qrCodeType']
        self.qrCodePath = wxconf.WXConf().baseconf['qrCodePath']
        self.session.headers.update({
            'User-Agent': ('Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.132 Safari/537.36'),
            'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8'
        })
        self.reLoginInfo()
        self.session.get(url='https://wx.qq.com/')

        pass

    # 登录
    def login(self):
        # print(self.getAuthStatus())
        if '200' in self.getAuthStatus():
            self.success("恢复登录成功")
            self.Listening()
            return
        self.getLoginCode()
        data = {
            'content': '请使用微信扫码登录邮件中的二维码',
            'image': self.image
        }
        wxmail.MyMail(data).run()
        self.sendDeviceId()
        self.waitForAuth()

    # 获取登录图片
    def getLoginCode(self):
        r = self.session.get(url="https://login.wx2.qq.com/jslogin?appid=wx782c26e4c19acffb&redirect_uri=https%3A%2F%2Fwx2.qq.com%2Fcgi-bin%2Fmmwebwx-bin%2Fwebwxnewloginpage&fun=new&lang=zh_CN&_="+str(int(round(time.time() * 1000))))
        self.uuid = re.search('uuid = "(.*?)"',r.text).group(1)
        if self.uuid:
            self.loadimage("https://login.weixin.qq.com/qrcode/"+self.uuid)

    # 下载图片
    def loadimage(self,imgUrl):
        r = self.session.get(imgUrl,stream=True)
        if self.qrCodeType == 'file':
            file = self.qrCodePath + 'qrcode.png'
            with open(file, 'wb') as f:
                for chunk in r.iter_content(chunk_size=32):
                    f.write(chunk)
            self.image = file
        elif self.qrCodeType == 'bytes':
            self.image = r.content

    # 等待登录
    def waitForAuth(self):
        try:
            x, y = 1, 1
            while True:
                time.sleep(3)
                authStatus = self.getAuthStatus()
                # self.notice(authStatus)
                if '408' in authStatus:
                    if x:
                        self.notice('等待二维码扫描及授权...')
                        x = -2
                elif '201' in authStatus:
                    if y:
                        self.notice('二维码已扫描，等待授权...')
                        y = -2
                elif '二维码已失效' in authStatus:
                    self.error('二维码已失效, 重新获取二维码')
                    self.login()
                    x, y = 1, 1
                elif '200' in authStatus:
                    # 获取登录返回的参数
                    p = self.getUrlParse(authStatus)
                    self.notice('已获授权')
                    self.getUserInfo(p)
                    self.saveLoginInfo()
                    self.Listening()
                    break
                else:
                    self.error('获取二维码扫描状态时出错, html="%s"', authStatus)
                    sys.exit(1)
        except Exception as e:
            self.error("登录时出错：",e)
        pass

    # 登录状态
    def getAuthStatus(self):
        result = self.session.get(url='https://login.wx.qq.com/cgi-bin/mmwebwx-bin/login?loginicon=true&uuid='
                                      +self.uuid+'&tip=0&r=-1536534515&_='+str(int(time.time()*1000)))
        return result.content.decode('utf8')

    # 产生随机设备信息
    def getDeviceID(self):
        DeviceID = "e"
        for i in range(0,15):
            DeviceID += str(random.randint(0,9))
        return DeviceID

    # 发送设备信息
    def sendDeviceId(self):
        self.deviceId = self.getDeviceID()
        data = {
            'BaseRequest':{"Uin": "", "Sid": "", "DeviceID": self.deviceId},
            'Count':0,
            'List':[]
        }
        self.session.post(url='https://wx.qq.com/cgi-bin/mmwebwx-bin/webwxstatreport?fun=new'
                          ,data=data)

    # 获取登录用户信息
    def getUserInfo(self, parse):
        data = {
            "ticket": parse['ticket'],
            "uuid": parse['uuid']+'==',
            "lang": parse['lang'],
            "scan": parse['scan'],
            "fun": "new",
            "version": "v2"
        }
        self.lang = parse['lang']
        url = self.getUrlCombin(domain="https://wx2.qq.com/cgi-bin/mmwebwx-bin/webwxnewloginpage", data=data)
        r = self.sendGet(url=url)
        self.notice(r.content)
        self.loginInfo = {
            'ret': re.search('<ret>(.*?)</ret>', str(r.content)).group(1),
            'message': re.search('<message>(.*?)</message>', str(r.content)).group(1),
            'skey': re.search('<skey>(.*?)</skey>', str(r.content)).group(1),
            'wxsid': re.search('<wxsid>(.*?)</wxsid>', str(r.content)).group(1),
            'wxuin': re.search('<wxuin>(.*?)</wxuin>', str(r.content)).group(1),
            'pass_ticket': re.search('<pass_ticket>(.*?)</pass_ticket>', str(r.content)).group(1),
            'isgrayscale': re.search('<isgrayscale>(.*?)</isgrayscale>', str(r.content)).group(1)
        }
        self.pass_ticket = re.search('<pass_ticket>(.*?)</pass_ticket>', str(r.content)).group(1)
        self.cookie = r.cookies

    # 恢复登录信息
    def reLoginInfo(self):
        try:
            info = self.mydb.getLoginInfo()
            # print(info)
            self.uuid = info[5]
            self.session.headers.update({
                'Cookie': info[4]
            })
            # print(info[5])
        except Exception as e:
            self.error("恢复登录未成功")
        # self.notice(self.session.headers)
        # self.notice(info[5])
        pass


    # 保存登录信息
    def saveLoginInfo(self):
        cookiestr = ""
        for k,v in self.cookie.items():
            cookiestr += k+'='+v + '; '
        self.notice(cookiestr[:-2])
        self.mydb.saveLoginInfo(uin=self.loginInfo["wxuin"],sid=self.loginInfo["wxsid"],skey=self.loginInfo['skey'],deviceID=self.deviceId,session=cookiestr[:-2],uuid=self.uuid, lang=self.lang, pass_ticket=self.pass_ticket)

        pass

    # 监听消息
    def Listening(self):
        try:
            info = self.mydb.getLoginInfo()
            uin = info[0]
            sid = info[1]
            skey = info[2]
            deviceid = info[3]
            lang = info[6]
            pass_ticket = info[7]
            data = {
                'r': str(int(time.time()*1000)),
                'skey': skey,
                'sid': sid,
                'uin': uin,
                'deviceid': deviceid,
                'synckey': '1_685070455 | 2_685071073 | 3_685071002 | 11_685070705 | 201_1547877849 | 1000_1547874121 | 1001_1547874195',
                '_': str(int(time.time()*1000)+100000)
            }
            url = self.getUrlCombin("https://webpush.wx2.qq.com/cgi-bin/mmwebwx-bin/synccheck",data=data)
            while True:
                time.sleep(3)
                r = self.session.get(url=url,timeout=25)
                # self.notice(r.text)
                # self.notice(re.search('selector:"(.*?)"', r.text).group(1))
                # self.notice(pass_ticket)
                # self.notice(info)
                print(r.text)
                if '1101' in r.text:
                    self.notice("你已经退出微信登录")
                    self.mydb.delLoginInfo(uin=uin)
                    return
                if re.search('selector:"(.*?)"',r.text).group(1) != '0':
                    # self.notice(uin, sid, skey, deviceid, lang, pass_ticket)
                    self.notice(self.GetMsg(uin, sid, skey, deviceid,lang, pass_ticket))
                    pass
        except Exception as e:
            self.error("监听微信消息时出错：",e)
        pass

    # 获取信息
    def GetMsg(self,Uin,Sid,Skey,DeviceId,Lang,Pass_ticket):
        data = {
            "BaseRequest": {
                "Uin": Uin,
                "Sid": Sid,
                "Skey": Skey,
                "DeviceID": DeviceId
            },
            "SyncKey": {
                "Count": 7,
                "List": "[{'Key': '1', 'Val': '685070455'},{'Key': '2', 'Val': '685071133'},{'Key': '3', 'Val': '685071002'},{'Key': '11', 'Val': '685070705'},{'Key': '201', 'Val': '1547882993'},{'Key': '1000', 'Val': '1547877661'},{'Key': '1001', 'Val': '1547874195'}]",
                'rr': '-1694788108'
            }
        }
        urldata = {
            "sid": Sid,
            "skey": Skey,
            "lang": Lang,
            "pass_ticket": Pass_ticket
        }
        url = self.getUrlCombin("https://wx2.qq.com/cgi-bin/mmwebwx-bin/webwxsync",data=urldata)
        return self.sendPost(url=url,data=data).text
        pass

    # 解析url参数
    def getUrlParse(self, url):
        res = {}
        uri = re.search('redirect_uri="(.*?)"', url).group(1)
        for i in uri.split('?')[1].split('&'):
            res[i.split('=')[0]] = i.split('=')[1]
        return res

    # 组合url参数
    def getUrlCombin(self,domain,data):
        url = domain + '?'
        for k, v in data.items():
            url += k + '=' + v + '&'
        return url[:-1]

    # 发送post请求
    def sendPost(self, url, data):
        return self.session.post(url=url,data=data)

    # 发送GET请求
    def sendGet(self,url):
        return self.session.get(url=url)


if __name__ == '__main__':
    wx = parse()
    # wx.getLoginCode()
    wx.getDeviceID()
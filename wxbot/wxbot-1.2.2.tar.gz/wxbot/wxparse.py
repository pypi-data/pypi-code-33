# -*- coding:utf-8 -*-
import json
import math
import random
import gzip
__authon__ = "cfn@leapy.cn"

import requests
from wxbot import wxmessage,wxconf,wxmail
import time
import re
import sys

class parse(wxmessage.message):
    def __init__(self):
        wxmessage.message.__init__(self)
        self.session = requests.session()
        self.session.headers.update({
            'User-Agent': ('Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.132 Safari/537.36'),
            'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8'
        })
        self.qrCodeType = wxconf.WXConf().baseconf['qrCodeType']  #二维码类型
        self.qrCodePath = wxconf.WXConf().baseconf['qrCodePath']  #二维码路径
        self.image = ""    # qrcode
        self.uuid = ""     # uuid
        self.authStatus = ""  # 登录状态信息
        self.deviceID = ""
        self.wxsid = ""
        self.skey = ""
        self.wxuin = ""
        self.cookies = ""
        self.userInfo = "" #用户信息
        self.flow = 0
    pass

    # 获取UUID
    def GetUUId(self):
        url = "https://login.wx2.qq.com/jslogin?appid=wx782c26e4c19acffb&redirect_uri=https%3A%2F%2Fwx2.qq.com%2Fcgi-bin%2Fmmwebwx-bin%2Fwebwxnewloginpage&fun=new&lang=zh_CN&_=" + str(
            int(round(time.time() * 1000)))
        r = self.session.get(url=url).text
        code = re.search("window.QRLogin.code = (.*?);",r).group(1)
        uuid = re.search('window.QRLogin.uuid = "(.*?)"',r).group(1)
        self.startTime = int(time.time() * 1000)
        if code == "200":
            self.flow += 1
            self.uuid = uuid
        else:
            self.flow = 0
            self.uuid = 0

    # 获取二维码 根据配置获取图片类型
    def GetQrCode(self):
        url = "https://login.weixin.qq.com/qrcode/"+self.uuid
        if self.qrCodeType == 'file':
            r = self.session.get(url=url)
            file = self.qrCodePath + 'qrcode.png'
            with open(file, 'wb') as f:
                for chunk in r.iter_content(chunk_size=32):
                    f.write(chunk)
            self.image = file
            self.flow += 1
            return file
        elif self.qrCodeType == 'bytes':
            r = self.session.get(url=url, stream=True)
            self.image = r.content
            self.flow += 1
            return r.content
        self.flow = 0
        pass

    # 发送邮件
    def SendMail(self):
        data = {
            'content': '请使用微信扫码登录邮件中的二维码',
            'image': self.image
        }
        if wxmail.MyMail(data).run():
            self.flow += 1
        else:
            self.flow = 0
        pass

    # 发送设备ID
    def SendDeviceID(self):
        url = "https://wx2.qq.com/cgi-bin/mmwebwx-bin/webwxstatreport?fun=new&lang=zh_CN"
        data = {
            "BaseRequest": self.BaseRequestsInit(),
            "Count": "2",
            "List": [
                {
                    "Text": {
                        "type":"[app - runtime]",
                        "data":
                            {
                                "unload":
                                    {
                                        "listenerCount":117,
                                        "watchersCount":115,
                                        "scopesCount":30
                                    }
                            }
                    },
                    "Type": 1
                },
                {
                    "Text":
                        {
                            "type":
                                "[app - timing]",
                            "data":
                                {
                                    "appTiming":
                                        {
                                            "qrcodeStart": self.startTime,
                                            "qrcodeEnd":  self.startTime+200
                                        },
                                    "pageTiming":
                                        {
                                            "navigationStart": self.startTime - 600,
                                            "unloadEventStart": 0,
                                            "unloadEventEnd": 0,
                                            "redirectStart": 0,
                                            "redirectEnd": 0,
                                            "fetchStart": self.startTime - 500,
                                            "domainLookupStart": self.startTime - 500,
                                            "domainLookupEnd": self.startTime - 500,
                                            "connectStart": self.startTime - 500,
                                            "connectEnd": self.startTime - 500,
                                            "secureConnectionStart": 0,
                                            "requestStart": self.startTime - 496,
                                            "responseStart": self.startTime - 497,
                                            "responseEnd": self.startTime - 460,
                                            "domLoading": self.startTime - 468,
                                            "domInteractive": self.startTime - 99,
                                            "domContentLoadedEventStart": self.startTime - 96,
                                            "domContentLoadedEventEnd": self.startTime - 82,
                                            "domComplete": self.startTime - 2,
                                            "loadEventStart": self.startTime - 2,
                                            "loadEventEnd": self.startTime - 2
                                        }
                                }
                        },
                    "Type": 1
                }
            ]
        }
        self.session.post(url=url,data=data)
        self.flow += 1
        pass

    # 获取扫码登录状态
    def GetAuthStatus(self):
        self.authStatus = self.session.get(url='https://login.wx.qq.com/cgi-bin/mmwebwx-bin/login?loginicon=true&uuid='
                                      +self.uuid+'&tip=0&_='+str(int(time.time()*1000))).text

    # 获取登录信息
    def GetLoginInfo(self):
        url = re.search('redirect_uri="(.*?)";', self.authStatus).group(1) + "&fun=new&version=v2"
        # self.notice(url)
        r = self.session.get(url=url)
        self.ret = re.search("<ret>(.*?)</ret>",r.text).group(1)
        self.skey = re.search("<message>(.*?)</message>", r.text).group(1)
        self.skey = re.search("<skey>(.*?)</skey>", r.text).group(1)
        self.wxsid = re.search("<wxsid>(.*?)</wxsid>",r.text).group(1)
        self.wxuin = re.search("<wxuin>(.*?)</wxuin>", r.text).group(1)
        self.pass_ticket = re.search("<pass_ticket>(.*?)</pass_ticket>", r.text).group(1)
        self.isgrayscale = re.search("<isgrayscale>(.*?)</isgrayscale>", r.text).group(1)
        self.cookies = r.cookies
        self.flow += 1
        pass

    # 等待扫码登录
    def waitForAuth(self):
        try:
            x, y = 1, 1
            while True:
                time.sleep(3)
                self.GetAuthStatus()
                if '408' in self.authStatus:
                    if x:
                        self.notice('等待二维码扫描及授权...')
                        x = -2
                elif '201' in self.authStatus:
                    if y:
                        self.notice('二维码已扫描，等待授权...')
                        y = -2
                elif '二维码已失效' in self.authStatus:
                    self.error('二维码已失效, 重新获取二维码')
                    self.login()
                    x, y = 1, 1
                elif '200' in self.authStatus:
                    self.notice('已获授权')
                    self.flow += 1
                    break
                else:
                    self.error('获取二维码扫描状态时出错, html="%s"', self.authStatus)
                    raise RuntimeError('获取二维码时出错')
        except Exception as e:
            self.flow = 0
            self.error("登录时出错：", e)
        pass

    def BaseRequestsInit(self):
        return {
            "DeviceID": self.deviceID,
            "Sid": self.wxsid,
            "Skey": self.skey,
            "Uin": self.wxuin
        }

    def GetR(self, length=10):
        if length <= 15:
            end = 2 + length
            return int(repr(random.random())[2:end])
        else:
            num = ''
            loop_times = math.floor(length / 15)
            need_more = length % 15
            for k in range(loop_times):
                num += repr(random.random())[2:17]
            end = 2 + need_more
            num += repr(random.random())[2:end]
            return int(num)

    def CookieInit(self):
        c = requests.cookies.RequestsCookieJar()
        c.set('MM_WX_NOTIFY_STATE', '1')
        c.set('MM_WX_SOUND_STATE', '1')
        c.set('webwx_data_ticket', self.cookies['webwx_data_ticket'])
        c.set('wxuin', self.cookies['wxuin'])
        c.set('mm_lang', self.cookies['mm_lang'])
        c.set('wxsid', self.cookies['wxsid'])
        c.set('webwx_auth_ticket', self.cookies['webwx_auth_ticket'])
        c.set('webwxuvid', self.cookies['webwxuvid'])
        c.set('wxloadtime', self.cookies['wxloadtime'])
        c.set('login_frequency', '1')
        c.set('last_wxuin', "")
        self.session.cookies.update(c)
        pass


    # 微信初始化
    def WXInit(self):
        url = "https://wx2.qq.com/cgi-bin/mmwebwx-bin/webwxinit?lang=zh_CN&r="+str(self.GetR())+"&lang=zh_CN&pass_ticket="+self.pass_ticket
        self.session.headers.update({
            "Accept": "application/json,text/plain, */*",
            "Content-Type": "application/json;charset=UTF-8",
            "Host": "wx2.qq.com",
            "Origin": "https://wx2.qq.com",
            "Referer": "https://wx2.qq.com/?&lang=zh_CN"

        })
        data = {
            "BaseRequest": self.BaseRequestsInit()
        }
        self.CookieInit()
        r = self.session.post(url=url, data=json.dumps(data), headers=self.session.headers)
        if r.text:
            self.userInfo = json.loads(r.text)['User']
            self.syncKey = json.loads(r.text)['SyncKey']
            self.flow += 1
        else:
            self.flow = 0

    # 微信状态通知
    def webwxstatusnotify(self):
        # self.notice(self.userInfo['UserName'])
        url = "https://wx2.qq.com/cgi-bin/mmwebwx-bin/webwxstatusnotify"
        data = {
            'BaseRequest': self.BaseRequestsInit(),
            'ClientMsgId': int(time.time()*1000),
            'Code': 3,
            'FromUserName': self.userInfo['UserName'],
            'ToUserName': self.userInfo['UserName'],
        }
        r = self.session.post(url=url, data=json.dumps(data))
        self.flow += 1
        # self.notice(r.text)
        pass

    # 消息检查数据 ，第一次和之后不一样
    def SyncCheckData(self, synckey):
        s = ""
        for _ in synckey['List']:
            s += str(_['Key']) + '_' + str(_['Val']) + '%7C'

        data = {
            'r': str(int(time.time() * 1000)),
            'skey': self.skey.replace("@","%40"),
            'sid': self.wxsid,
            'uin': self.wxuin,
            'deviceid': self.deviceID,
            'synckey': s[:-3],
            '_': str(int(time.time() * 1000) + 100000)
        }
        return data

    # 消息检查
    def SyncCheck(self):
        url = "https://webpush.wx2.qq.com/cgi-bin/mmwebwx-bin/synccheck"
        try:
            while True:
                time.sleep(3)
                # self.notice(self.getUrlCombin(url, self.SyncCheckData(self.syncKey)))
                self.CookieInit()
                r = self.session.get(url=self.getUrlCombin(url, self.SyncCheckData(self.syncKey)))
                # self.notice(r.text)
                selector = re.search('selector:"(.*?)"', r.text).group(1)
                retcode = re.search('retcode:"(.*?)"', r.text).group(1)
                # self.notice(selector,retcode)
                if retcode == '0' and selector == '2':
                    # self.notice("发现新消息")
                    self.GetNewMsg()
                elif retcode == '0' and selector == '7':
                    self.notice("进入或者离开状态")
                elif retcode == '1101' or retcode == '1102':
                    self.notice("您已退出登录，或未登录此设备")
                    raise RuntimeError("")
                self.notice(time.strftime('%Y-%m-%d %H:%M:%S'))
        except Exception as e:
            self.error("检查消息时出错：", e)
        pass

    # 获取最新微信消息
    def GetNewMsg(self):
        url = "https://wx2.qq.com/cgi-bin/mmwebwx-bin/webwxsync?sid="+self.wxsid+"&skey="+self.skey+"&lang=zh_CN&pass_ticket="+self.pass_ticket
        data = {
            'BaseRequest': self.BaseRequestsInit(),
            'SyncKey': self.syncKey,
            'rr': ~int(time.time())
        }
        self.CookieInit()
        self.session.headers.update({
            "Accept": "application/json,text/plain, */*"
        })
        try:
            r = self.session.post(url=url, data=json.dumps(data),timeout=60)
            # print(r.text)
            r.encoding = 'utf-8'
            if r.text:
                msgList = json.loads(r.text)['AddMsgList']
                # self.notice(msgList)
                for _ in msgList:
                    if _['MsgType'] == 1:
                        self.notice("获取到消息：", _['Content'])
                        self.syncKey = json.loads(r.text)['SyncKey']
                    elif _['MsgType'] == 47:
                        self.notice("获取到消息：", "[发送了一个表情，请在手机上查看]")
                    elif _['MsgType'] == 51:
                        self.notice("初始化")
                        pass
        except:
            pass

    # 获取
    def GetDeviceID(self):
        DeviceID = "e"
        for i in range(0, 15):
            DeviceID += str(random.randint(0, 9))
        self.deviceID = DeviceID
        self.flow += 1

    # 组合url参数
    def getUrlCombin(self, domain, data):
        url = domain + '?'
        for k, v in data.items():
            url += k + '=' + v + '&'
        return url[:-1]

    # 退出登录
    def QuitLogin(self):
        if self.flow == 0:
            self.notice("未登录，已退出")
        else:
            url = "https://wx2.qq.com/cgi-bin/mmwebwx-bin/webwxlogout?redirect=1&type=0&skey=" + self.skey
            data = {
                'sid': self.wxsid,
                'uin': self.wxuin
            }
            self.session.post(url=url, data=json.dumps(data))
            self.flow = 0
        pass

    # 登录
    def login(self):
        try:
            if self.flow != 0:
                raise RuntimeError('初始化时出错')
            self.GetUUId()
            if self.flow != 1:
                raise RuntimeError('获取uuid时出错')
            self.GetDeviceID()
            if self.flow != 2:
                raise RuntimeError('获取设备ID时出错')
            self.SendDeviceID()
            if self.flow != 3:
                raise RuntimeError('发送设备信息时出错')
            self.GetQrCode()
            if self.flow != 4:
                print(self.flow)
                raise RuntimeError('获取二维码时出错')
            self.SendMail()
            if self.flow != 5:
                raise RuntimeError('发送邮件时出错')
            self.waitForAuth()
            if self.flow != 6:
                raise RuntimeError('等待登录验证时出错')
            self.GetLoginInfo()
            if self.flow != 7:
                raise RuntimeError('获取用户信息时出错')
            self.WXInit()
            if self.flow != 8:
                raise RuntimeError('Webwx初始化时出错')
            self.webwxstatusnotify()
            if self.flow != 9:
                raise RuntimeError('发送登录状态时出错')
            self.SyncCheck()
            if self.flow != 10:
                raise RuntimeError('消息检查时出错')
        except Exception as e:
            self.error("程序已停止,错误如下：", e)
            sys.exit(-1)

    # 重新登录
    def ReLogin(self):

        pass


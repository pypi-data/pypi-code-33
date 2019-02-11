# -*- coding:utf-8 -*-
"""
FileName: webapiconf.py
Version: 0.1
Company: cninfo
Author: ruitian.chen
Create Date: 2019-02-11
Description: webapi请求参数配置文件.重要配置项均从该程序获取
History: /*
 create 2019-02-11
 */
"""
import os
from enum import Enum
from configparser import ConfigParser


class SaveType(Enum):
    CSV = 1       # CSV文件
    EXCEL = 2     # EXCEL文件
    JSON = 3      # JSON格式文件
    HDF5 = 4      # HDF5文件
    DATABASE = 5  # 关系数据库
    NOSQL = 6     # nosql数据库
    CONSOLE = 7   # 直接打印
    NONE = 9      # 啥也没有


CLIENT_CURRENT_PATH = os.path.abspath(os.path.dirname(__file__))
# 获取cninfo-data-platform，也就是项目的根路径
CLIENT_ROOT_PATH = CLIENT_CURRENT_PATH[:CLIENT_CURRENT_PATH.find("cninfowebapi\\")+len("cninfowebapi\\")]

# 客户端默认的数据保存方式为CSV，用户可以根据自己需要进行设置，支持SaveType中列出的类型
CLIENT_SAVE_TYPE = SaveType.CSV

SESSION_CONF_FILEPATH = CLIENT_ROOT_PATH + '\\conf\\'


class WebApiConfig:
    """API最主要的配置文件"""
    __conf = ConfigParser()
    __sectionserver = 'serverinfo'
    __sectionclient = 'clientinfo'
    # 配置文件全路径
    __conffilename = SESSION_CONF_FILEPATH + 'cninfowebapi.cfg'
    __confitemserver = {}   # 服务端相关的配置项
    __confitemclient = {}   # 客户端相关的配置项

    def __init__(self):
        if not os.path.exists(self.__conffilename):
            self.creatconf()
            self.__conf.read(self.__conffilename)
            self.__conf.add_section(self.__sectionserver)
            self.__conf.add_section(self.__sectionclient)
            self.initdefaultconf()
            self.saveconf()
        self.loaddata()

    def loaddata(self):
        """加载配置文件"""
        self.__conf.read(self.__conffilename)
        confdictserver = dict(self.__conf.items(self.__sectionserver))
        for confitem in confdictserver.keys():
            self.__confitemserver[confitem.upper()] = str(self.__conf.get(self.__sectionserver, confitem))
        confdictclient = dict(self.__conf.items(self.__sectionclient))
        for confitem in confdictclient.keys():
            self.__confitemserver[confitem.upper()] = str(self.__conf.get(self.__sectionclient, confitem))

    def initdefaultconf(self):
        """如果不存在配置文件，则初始化配置项的值"""
        # 默认访问webapi测试环境
        self.setserverconf('API_SERVER_URL', 'http://api1.before.com:9091')
        # CLIENT_SAVE_ENGINE = 'mysql://cninfo:cninfo@127.0.0.1/infodb?charset=utf8'
        # 默认存储sqllite数据库, 可以改为mysql\oracle\postgresql等
        self.setclientconf('CLIENT_SAVE_FILEPATH', CLIENT_ROOT_PATH + '\\data\\')
        # 默认保存数据库的方式为sqlite
        self.setclientconf('CLIENT_SAVE_ENGINE', 'sqlite:///' + CLIENT_ROOT_PATH + '\\data\\apidb.db')
        self.setclientconf('USER_CLIENT_ID', '0ddc14c30d7f4cd1b30261263cb376eb')
        self.setclientconf('USER_CLIENT_SECRET', 'e8cb33ca4aad49a4a742794fd892fd91')

    def creatconf(self):
        """创建配置文件目录和文件"""
        if not os.path.exists(SESSION_CONF_FILEPATH):
            os.makedirs(SESSION_CONF_FILEPATH)
        with open(self.__conffilename, 'w') as fw:
            self.__conf.write(fw)

    def saveconf(self):
        """保存数据到配置文件"""
        for confitem in self.__confitemserver.keys():
            self.__conf.set(self.__sectionserver, confitem, str(self.__confitemserver[confitem]))
        for confitem in self.__confitemclient.keys():
            self.__conf.set(self.__sectionclient, confitem, str(self.__confitemclient[confitem]))
        self.creatconf()

    def setserverconf(self, itemname, itemvalue):
        self.__conf.set(self.__sectionserver, itemname.upper(), str(itemvalue))
        self.__confitemserver[itemname.upper()] = itemvalue

    def getserverconf(self, itemname):
        confval = ''
        if itemname in self.__confitemserver.keys():
            confval = self.__confitemserver[itemname]
        else:
            confval = self.__conf.get(self.__sectionserver, itemname)
            self.__confitemserver[itemname.upper()] = confval
        return str(confval)

    def setclientconf(self, itemname, itemvalue):
        self.__conf.set(self.__sectionclient, itemname.upper(), str(itemvalue))
        self.__confitemclient[itemname.upper()] = itemvalue

    def getclientconf(self, itemname):
        if itemname in self.__confitemclient.keys():
            confval = self.__confitemclient[itemname]
        else:
            confval = self.__conf.get(self.__sectionclient, itemname)
            self.__confitemserver[itemname.upper()] = confval
        return str(confval)

    def printconfinfo(self):
        print('=====================项目主要配置项======================')
        print('CLIENT_ROOT_PATH' + '=' + CLIENT_ROOT_PATH)
        print('SESSION_CONF_FILEPATH' + '=' + SESSION_CONF_FILEPATH)
        print('CLIENT_SAVE_TYPE' + '=' + str(CLIENT_SAVE_TYPE))
        for confitem in self.__confitemserver.keys():
            print(confitem + '=' + self.getserverconf(confitem))
        for confitem in self.__confitemclient.keys():
            print(confitem + '=' + self.getclientconf(confitem))
        print('=========================================================')


webapiconf = WebApiConfig()


if __name__ == '__main__':
    webapiconf.printconfinfo()

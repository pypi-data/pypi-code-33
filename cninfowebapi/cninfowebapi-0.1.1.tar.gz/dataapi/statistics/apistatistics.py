# -*- coding:utf-8 -*-
"""
FileName: apistaticstics.py
Version: 0.1
Company: cninfo
Author: ruitian.chen
Create Date: 2019-01-30
Description: API访问统计.
History: /*
 create 2019-01-30
 */
"""
import os
import configparser
from dataapi.conf.clientinfo import SESSION_CONF_FILEPATH


class APIStatistics:
    """API访问次数统计类
    统计误差小于100次：每调用100次API保存一次统计计数，因此当一个会话期间调用小于100次需要用户自己调用apistat.saveconf()
    进行保存，否则仅在每调用100次的节点自动保存文件，如 100,200,300,...,100*N
    """
    __conf = configparser.ConfigParser()
    __apidict = {}
    __sectionname = 'apistat'
    # 配置文件全路径
    __conffilename = SESSION_CONF_FILEPATH + 'apitatistics.ini'
    # API调用计数器，用于判断超过100次保存一次文件
    __apicall_counter = 0

    def __init__(self):
        if not os.path.exists(self.__conffilename):
            self.creatconf()
            self.__conf.read(self.__conffilename)
            self.__conf.add_section(self.__sectionname)
            self.saveconf()
        self.loaddata()

    def loaddata(self):
        """加载配置文件到API统计字典"""
        self.__conf.read(self.__conffilename)
        apidict = dict(self.__conf.items(self.__sectionname))
        for api in apidict.keys():
            self.__apidict[api] = self.__conf.getint(self.__sectionname, api)

    def getapivisitinfo(self):
        return self.__apidict

    def getapivisitcount(self, apiname):
        """获取某个API已有访问次数"""
        vcount = 0
        if apiname in self.__apidict.keys():
            vcount = self.__apidict[apiname] = self.__apidict[apiname]
        return vcount

    def visitapi(self, apiname):
        """访问API计数"""
        self.__apidict[apiname] = self.getapivisitcount(apiname) + 1
        self.__apicall_counter += 1
        if self.__apicall_counter >= 100:
            self.saveconf()

    def creatconf(self):
        with open(self.__conffilename, 'w') as fw:
            self.__conf.write(fw)

    def saveconf(self):
        """保存数据到配置文件"""
        totalcount = 0
        for api in self.__apidict.keys():
            self.__conf.set(self.__sectionname, api, str(self.__apidict[api]))
            if api != 'all_count':
                totalcount = totalcount + self.__apidict[api]
        self.__conf.set(self.__sectionname, 'all_count', str(totalcount))
        self.creatconf()


apistat = APIStatistics()


if __name__ == '__main__':
    print(apistat.getapivisitinfo())
    apistat.visitapi('p_info3011')
    apistat.visitapi('p_info3012')
    apistat.visitapi('p_info3013')
    apistat.visitapi('p_info3014')
    apistat.visitapi('p_info3015')
    apistat.visitapi('p_info3011')
    print('================================')
    print(apistat.getapivisitinfo())
    apistat.saveconf()

# -*- coding:utf-8 -*-
"""
FileName: store.py
Version: 0.1
Company: cninfo
Author: ruitian.chen
Create Date: 2019-01-28
Description: 存储请求到的数据
History: /*
 create 2019-01-28
 */
"""
import time
import simplejson as json
import pymongo
from dataapi.conf.clientinfo import SaveType, CLIENT_SAVE_ENGINE, CLIENT_SAVE_FILEPATH, CLIENT_SAVE_TYPE
from sqlalchemy import create_engine
from dataapi.client import apiclient
from dataapi.conf.apilog import logger


class DataMart:
    """
    数据超市类，获取API数据的入口。
    用户可以通过该类的 getdata(apiname, paramsdict) 方法获取api数据，只需要提供api名称和必要的参数字典即可。
    对于获取到的数据自动完成存储。
    """
    __savetype = SaveType.EXCEL
    __savepath = CLIENT_SAVE_FILEPATH
    __engine = create_engine(CLIENT_SAVE_ENGINE)
    __reqcount = 0

    def __init__(self, savatype=SaveType.EXCEL, savepath=CLIENT_SAVE_FILEPATH):
        self.__savetype = savatype
        self.__savepath = savepath
        self.__engine = create_engine(CLIENT_SAVE_ENGINE)

    def apihelp(self, apiname):
        """ API帮助信息
        ----------
        @param apiname : string
        @return 无返回值，仅打印输入API的描述、输入参数、返回字段信息。
        """
        print("=================================================================================")
        print('API描述：' + json.dumps(apiclient.getapidesc(apiname), ensure_ascii=False, indent=4))
        print("-----------------------------------API请求参数-----------------------------------")
        print("isNeed: 是否必填参数 | fieldName: 参数名称 | fieldType: 参数数据类型 | defaultValue: 默认值 | checkRule:参数校验规则 | describe:参数描述 | fieldChineseName: 参数中文名 ")
        print(json.dumps(json.loads(apiclient.getapiparaminfo(apiname)), ensure_ascii=False, indent=4))
        print("-----------------------------------API返回字段-----------------------------------")
        print("describe:字段描述 | fieldChineseName: 字段中文名 | fieldName: 字段名称 | fieldType: 字段数据类型")
        print(json.dumps(json.loads(apiclient.getapicolinfo(apiname)), ensure_ascii=False, indent=4))
        print("=================================================================================")

    def setSaveType(self, type):
        """设置API数据保存格式"""
        logger.info('Set savetype to ' + str(type))
        self.__savetype = type

    def getapidata(self, apiname, paramsdict={}):
        """ API数据获取
         ----------
        @param apiname: string  API名称
        @param paramsdict: dict  API请求参数字典
        @return df: pandas.DataFrame  API返回的数据
        """
        print('API URL：' + apiclient.getapifullurl(apiname, paramsdict))
        df = apiclient.reqapi(apiname, params=paramsdict)
        self.savedata(df, apiname)
        self.__reqcount += 1
        return df

    def getfilesuffixname(self):
        """ 获取保存文件名称后缀"""
        qtime = time.strftime("%Y%m%d_%H%M%S", time.localtime())
        suffix = '_' + qtime + '_' + str(self.__reqcount)
        return suffix

    def savedata(self, df, targetname):
        """ API数据保存
        ----------
        @param df: df: pandas.DataFrame  API返回数据
        @param targetname: string  保存名称
        @return 无返回
        """
        if self.__savetype == SaveType.CSV:
            self.stavetocsv(df, targetname)
        elif self.__savetype == SaveType.EXCEL:
            self.savetoxls(df, targetname)
        elif self.__savetype == SaveType.JSON:
            self.savetojson(df, targetname)
        elif self.__savetype == SaveType.HDF5:
            self.savetohdf(df, targetname)
        elif self.__savetype == SaveType.DATABASE:
            self.savetodb(df, targetname)
        elif self.__savetype == SaveType.CONSOLE:
            self.printconsole(df, targetname)
        elif self.__savetype == SaveType.NOSQL:
            self.savetomongo(df, targetname)
        else:
            pass
        logger.info('Save api to File  ' + targetname)

    def stavetocsv(self, df, targetname):
        """保存为CSV格式文件"""
        df.to_csv(self.__savepath + targetname + self.getfilesuffixname() + '.csv')

    def savetoxls(self, df, targetname):
        """保存为EXCEL格式文件"""
        df.to_excel(self.__savepath + targetname + self.getfilesuffixname() + '.xlsx')

    def savetojson(self, df, targetname):
        """保存为JSON格式文件"""
        df.to_json(self.__savepath + targetname + self.getfilesuffixname() + '.json')

    def savetohdf(self, df, targetname):
        """保存为HDF5格式文件"""
        df.to_hdf(self.__savepath + 'apidata.h5', targetname)

    def savetodb(self, df, targetname):
        """保存到关系数据库"""
        df.to_sql(targetname, self.__engine, if_exists='append', index=False)

    def savetomongo(self, df, targetname):
        """保存到mongo数据库"""
        # conn = pymongo.Connection('127.0.0.1', port=27017)
        # conn.db.'targetname'.insert(json.loads(df.to_json()))
        pass

    def printconsole(self, df, targetname):
        """输出到控制台"""
        print('From Shenzhenxin api {} get {} rows data exp:'.format(targetname, len(df)))
        print(df.head(20))


datamart = DataMart(savatype=CLIENT_SAVE_TYPE)


if __name__ == "__main__":
    datamart.getapidata('p_stock2100', paramsdict={'scode': '000001,600000'})

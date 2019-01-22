#!/usr/bin/env python
# -*- coding: utf-8 -*-

############################################################
#                                                           
# Copyright (C)2018 SenseDeal AI, Inc. All Rights Reserved  
#                                                           
############################################################

'''                                                       
File: .py
Author: xuwei                                        
Email: weix@sensedeal.ai                                 
Last modified: 2018.12.20 18:25 
Description:                                            
'''


#在ubuntu系统中开启服务时，把下面三行打开
# import sys
# import io
# sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')


import grpc
import json
from sense_data import stock_pb2_grpc, stock_pb2
from sense_data.dictobj import *
import sense_core as sd



class SenseDataService(object):

    def __init__(self, label='data_rpc'):
        self._host = sd.config(label, 'host')
        self._port = sd.config(label, 'port')

    #1
    @sd.catch_raise_exception
    def get_stock_price_tick(self, stock_code):
        with grpc.insecure_channel(self._host + ":" + self._port) as channel:
            stub = stock_pb2_grpc.StockInfStub(channel)
            response = stub.get_stock_price_tick(stock_pb2.Request(stock_code=stock_code))
            status = response.status
            if status.code == 2:
                sd.log_error("get_company_info return error:" + response.status.msg)
                return None
            result = json.loads(response.txt)
            result = StockPriceTickObj(result)
            return result

    #2
    @sd.catch_raise_exception
    def get_company_info(self, stock_code):
        with grpc.insecure_channel(self._host+":"+self._port,
                                   options=[('grpc.max_send_message_length', 30 * 1024 * 1024),
                                            ('grpc.max_receive_message_length', 30 * 1024 * 1024)]) as channel:
            stub = stock_pb2_grpc.StockInfStub(channel)
            stock_code = json.dumps(stock_code)
            response = stub.get_company_info(stock_pb2.Request(stock_code=stock_code))
            # print(response)
            status = response.status
            if status.code == 2:
                sd.log_error("get_company_info return error:" + response.status.msg)
                return None
        _list = json.loads(response.txt)
        if len(_list) == 1:
            _dct = CompanyInfoObj(_list[0])
            return _dct
        else:
            _dct_list = []
            for dct in _list:
                _dct_list.append(CompanyInfoObj(dct))
            return _dct_list

    #3
    @sd.catch_raise_exception
    def get_company_alias(self, stock_code):
        with grpc.insecure_channel(self._host+":"+self._port,
                                   options=[('grpc.max_send_message_length', 30 * 1024 * 1024),
                                            ('grpc.max_receive_message_length', 30 * 1024 * 1024)]) as channel:
            stub = stock_pb2_grpc.StockInfStub(channel)
            stock_code = json.dumps(stock_code)
            response = stub.get_company_alias(stock_pb2.Request(stock_code=stock_code))
            status = response.status
            if status.code == 2:
                sd.log_error("get_company_info return error:" + response.status.msg)
                return None
            _list = json.loads(response.txt)
            # print(_list[0])
            if len(_list) == 1:
                _obj = CompanyAliasObj(_list[0])
                return _obj
            else:
                _dct_list = []
                for dct in _list:
                    _dct_list.append(CompanyAliasObj(dct))
                return _dct_list

    #4
    @sd.catch_raise_exception
    def get_stock_price_day(self, *args):
        with grpc.insecure_channel(self._host+":"+self._port) as channel:
            stub = stock_pb2_grpc.StockInfStub(channel)
            if len(args) ==3:
                response = stub.get_stock_price_day(
                    stock_pb2.Request(var_num=len(args), stock_code=args[0], start_date=args[1], end_date=args[2]))
            elif len(args) ==2:
                response = stub.get_stock_price_day(
                    stock_pb2.Request(var_num=len(args), stock_code=args[0], start_date=args[1]))
            elif len(args) ==1:
                response = stub.get_stock_price_day(
                    stock_pb2.Request(var_num=len(args), stock_code=args[0]))
            status = response.status
            if status.code == 2:
                sd.log_error("get_stock_price_tick return error:" + response.status.msg)
                return None
            _list = json.loads(response.txt)
            if len(_list) == 1:
                _dct = StockPriceDayObj(_list[0])
                return _dct
            else:
                _dct_list = []
                for dct in _list:
                    _dct_list.append(StockPriceDayObj(dct))
                return _dct_list

    #5
    @sd.catch_raise_exception
    def get_subcompany(self, stock_code):
        with grpc.insecure_channel(self._host + ":" + self._port,
                                   options=[('grpc.max_send_message_length', 30 * 1024 * 1024),
                                            ('grpc.max_receive_message_length', 30 * 1024 * 1024)]
                                   ) as channel:
            stub = stock_pb2_grpc.StockInfStub(channel)
            stock_code = json.dumps(stock_code)
            response = stub.get_subcompany(stock_pb2.Request(stock_code=stock_code))
            status = response.status
            if status.code == 2:
                sd.log_error("get_company_info return error:" + response.status.msg)
                return None
            _list = json.loads(response.txt)
            if len(_list) == 1:
                _obj = SubcompanyInfoObj(_list[0])
                return _obj
            else:
                _dct_list = []
                for dct in _list:
                    _dct_list.append(SubcompanyInfoObj(dct))
                return _dct_list


    # @sd.try_catch_exception
    # def get_chairman_supervisor(self, company_code):
    #     with grpc.insecure_channel(self._host+":"+self._port) as channel:
    #         stub = stock_pb2_grpc.StockInfStub(channel)
    #         response = stub.get_chairman_supervisor(stock_pb2.Request(company_code=company_code))
    #         return list_to_object_list(response.msg)
    #
    # @sd.try_catch_exception
    # def get_stockholder(self, company_code):
    #     with grpc.insecure_channel(self._host+":"+self._port) as channel:
    #         stub = stock_pb2_grpc.StockInfStub(channel)
    #         response = stub.get_stockholder(stock_pb2.Request(company_code=company_code))
    #         return list_to_object_list(response.msg)
    #

    # @sd.try_catch_exception
    # def get_industry_concept(self, stock_code):
    #     with grpc.insecure_channel(self._host+":"+self._port) as channel:
    #         stub = stock_pb2_grpc.StockInfStub(channel)
    #         response = stub.get_industry_concept(stock_pb2.Request(stock_code=stock_code))
    #         return list_to_object_list(response.msg)
    #

if __name__ == '__main__':
    pass
    sesd = SenseDataService()
    # company_code = '10002320'
    # stock_code = '000002'
    # stock_code = []
    # stock_code = ['300144']
    stock_code = ['300144', '300167']
    # xw = sesd.get_stock_price_tick(stock_code) ##调试成功
    # xw = sesd.get_company_info(stock_code) ##调试成功

    # xw = sesd.get_stock_price_day(stock_code)  ##调试成功
    # xw = sesd.get_company_alias(stock_code)

    xw = sesd.get_subcompany(stock_code)
    print(type(xw))
    # print(len(xw))
    print(xw, '\n')
    # print(xw[0])
    # for key in xw[0].keys():
    #     print('self.{}'.format(key) + '=' 'dct[' + "'" + key + "']")





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
        sd.log_init_config('error_log', sd.config('log_path'))
    #1
    @sd.try_catch_exception
    def get_stock_price_tick(self, stock_code):
        try:
            with grpc.insecure_channel(self._host + ":" + self._port) as channel:
                stub = stock_pb2_grpc.StockInfStub(channel)
                response = stub.get_stock_price_tick(stock_pb2.Request(stock_code=stock_code))
                status = response.status
                if status.code == 2:
                    # sd.log_error("get_stock_price_tick return error:" + response.status.msg)
                    raise Exception(response.status.msg)
                result = json.loads(response.txt)
                return result
        except Exception as e:
            # sd.log_exception(e)
            raise e
    #1
    @sd.try_catch_exception
    def get_stock_price_tick_obj(self, stock_code):
        try:
            with grpc.insecure_channel(self._host + ":" + self._port) as channel:
                stub = stock_pb2_grpc.StockInfStub(channel)
                response = stub.get_stock_price_tick(stock_pb2.Request(stock_code=stock_code))
                status = response.status
                if status.code == 2:
                    # sd.log_error("get_stock_price_tick return error:" + response.status.msg)
                    raise Exception(response.status.msg)
                result = json.loads(response.txt)
                result = stock_price_tick_obj(result)
                return result
        except Exception as e:
            # sd.log_exception(e)
            raise e

    #2
    @sd.try_catch_exception
    def get_company_info(self, stock_code):
        try:
            with grpc.insecure_channel(self._host+":"+self._port,
                                       options=[('grpc.max_send_message_length', 30 * 1024 * 1024),
                                                ('grpc.max_receive_message_length', 30 * 1024 * 1024)]) as channel:
                stub = stock_pb2_grpc.StockInfStub(channel)
                stock_code = json.dumps(stock_code)
                response = stub.get_company_info(stock_pb2.Request(stock_code=stock_code))
                # print(response)
                status = response.status
                if status.code == 2:
                    # sd.log_error("get_company_info return error:" + response.status.msg)
                    raise Exception(response.status.msg)
            _list = json.loads(response.txt)
            if len(_list) == 1:
                _dct = company_info_obj(_list[0])
                return _dct
            else:
                _dct_list = []
                for dct in _list:
                    _dct_list.append(company_info_obj(dct))
                return _dct_list
        except Exception as e:
            # sd.log_exception(e)
            raise e

    #3
    @sd.try_catch_exception
    def get_company_alias(self, stock_code):
        try:
            with grpc.insecure_channel(self._host+":"+self._port,
                                       options=[('grpc.max_send_message_length', 30 * 1024 * 1024),
                                                ('grpc.max_receive_message_length', 30 * 1024 * 1024)]) as channel:
                stub = stock_pb2_grpc.StockInfStub(channel)
                stock_code = json.dumps(stock_code)
                response = stub.get_company_alias(stock_pb2.Request(stock_code=stock_code))
                status = response.status
                if status.code == 2:
                    # sd.log_error("get_company_info return error:" + response.status.msg)
                    raise Exception(response.status.msg)
                _list = json.loads(response.txt)
                # print(_list[0])
                if len(_list) == 1:
                    _obj = company_alias_obj(_list[0])
                    return _obj
                else:
                    _dct_list = []
                    for dct in _list:
                        _dct_list.append(company_alias_obj(dct))
                    return _dct_list
        except Exception as e:
            # sd.log_exception(e)
            raise e

    #4
    @sd.try_catch_exception
    def get_stock_price_day(self, *args):
        try:
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
                    # sd.log_error("get_stock_price_tick return error:" + response.status.msg)
                    raise Exception(response.status.msg)
                _list = json.loads(response.txt)
                if len(_list) == 1:
                    _dct = stock_price_day_obj(_list[0])
                    return _dct
                else:
                    _dct_list = []
                    for dct in _list:
                        _dct_list.append(stock_price_day_obj(dct))
                    return _dct_list
        except Exception as e:
            sd.log_exception(e)
            raise e

    #5
    @sd.try_catch_exception
    def get_subcompany(self, stock_code):
        try:
            with grpc.insecure_channel(self._host + ":" + self._port,
                                       options=[('grpc.max_send_message_length', 30 * 1024 * 1024),
                                                ('grpc.max_receive_message_length', 30 * 1024 * 1024)]
                                       ) as channel:
                stub = stock_pb2_grpc.StockInfStub(channel)
                stock_code = json.dumps(stock_code)
                response = stub.get_subcompany(stock_pb2.Request(stock_code=stock_code))
                status = response.status
                if status.code == 2:
                    # sd.log_error("get_company_info return error:" + response.status.msg)
                    raise Exception(response.status.msg)
                _list = json.loads(response.txt)
                if len(_list) == 1:
                    _obj = subcompany_info_obj(_list[0])
                    return _obj
                else:
                    _dct_list = []
                    for dct in _list:
                        _dct_list.append(subcompany_info_obj(dct))
                    return _dct_list
        except Exception as e:
            # sd.log_exception(e)
            raise e


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





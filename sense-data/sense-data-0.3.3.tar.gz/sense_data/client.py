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
import datetime
from sense_data import stock_pb2_grpc, stock_pb2
from sense_data.dictobj import *
import sense_core as sd
# sd.log_init_config('settings', sd.config('log_path'))
# print(sd.config('data_rpc', 'host'))


class SenseDataService(object):

    def __init__(self, label='data_rpc'):
        self._host = sd.config(label, 'host')
        self._port = sd.config(label, 'port')

#1
    @sd.catch_raise_exception
    def get_stock_price_tick(self, stock_code):
        with grpc.insecure_channel(self._host + ":" + self._port) as channel:
            _stub = stock_pb2_grpc.StockInfStub(channel)
            _response = _stub.get_stock_price_tick(stock_pb2.Request(stock_code=stock_code))
            _status = _response.status
            if _status.code != 0:
                sd.log_error("get_stock_price_tick return error:" + _status.msg)
                return None
            _result = json.loads(_response.txt)
            _result = StockPriceTickObj(_result)
            return _result

#2
    @sd.catch_raise_exception
    def get_company_info(self, code):
        with grpc.insecure_channel(self._host+":"+self._port,
                                   options=[('grpc.max_send_message_length', 30 * 1024 * 1024),
                                            ('grpc.max_receive_message_length', 30 * 1024 * 1024)]) as channel:
            _stub = stock_pb2_grpc.StockInfStub(channel)
            _stock_code = json.dumps(code)
            _response = _stub.get_company_info(stock_pb2.Request(stock_code=_stock_code))
            # print(_response)
            _status = _response.status
            if _status.code != 0:
                sd.log_error("get_company_info return error:" + _status.msg)
                return None
            _result_list = json.loads(_response.txt)
            if type(code) == str or len(code) == 1:
                _dct_one = CompanyInfoObj(_result_list[0])
                return _dct_one
            else:
                _dct_list = []
                for _dct in _result_list:
                    _dct_list.append(CompanyInfoObj(_dct))
                return _dct_list

#3
    @sd.catch_raise_exception
    def get_company_alias(self, code):
        with grpc.insecure_channel(self._host+":"+self._port,
                                   options=[('grpc.max_send_message_length', 30 * 1024 * 1024),
                                            ('grpc.max_receive_message_length', 30 * 1024 * 1024)]) as channel:
            _stub = stock_pb2_grpc.StockInfStub(channel)
            _stock_code = json.dumps(code)
            _response = _stub.get_company_alias(stock_pb2.Request(stock_code = _stock_code))
            _status = _response.status
            if _status.code != 0:
                sd.log_error("get_company_alias return error:" + _status.msg)
                return None
            _result_list = json.loads(_response.txt)
            # print(_result_list[0])
            if type(code) == str or len(code) == 1:
                _obj_one = CompanyAliasObj(_result_list[0])
                return _obj_one
            else:
                _dct_list = []
                for _dct in _result_list:
                    _dct_list.append(CompanyAliasObj(_dct))
                return _dct_list

#4
    @sd.catch_raise_exception
    def get_stock_price_day(self, *args):
        with grpc.insecure_channel(self._host + ":" + self._port,
                                   options=[('grpc.max_send_message_length', 30 * 1024 * 1024),
                                            ('grpc.max_receive_message_length', 30 * 1024 * 1024)]
                                   ) as channel:
            _stub = stock_pb2_grpc.StockInfStub(channel)
            if len(args) ==3:
                _response = _stub.get_stock_price_day(
                    stock_pb2.Request(var_num=len(args), stock_code=args[0], start_date=args[1], end_date=args[2]))
            elif len(args) ==2:
                _response = _stub.get_stock_price_day(
                    stock_pb2.Request(var_num=len(args), stock_code=args[0], start_date=args[1]))
            else:
                _response = _stub.get_stock_price_day(
                    stock_pb2.Request(var_num=len(args), stock_code=args[0]))
            _status = _response.status
            if _status.code != 0:
                sd.log_error("get_stock_price_day return error:" + _status.msg)
                return None
            _list = json.loads(_response.txt)
            if len(args) == 2:
                _dct = StockPriceDayObj(_list[0])
                return _dct
            else:
                _dct_list = []
                for _dct in _list:
                    _dct_list.append(StockPriceDayObj(_dct))
                return _dct_list

#5
    @sd.catch_raise_exception
    def get_subcompany(self, code):
        with grpc.insecure_channel(self._host + ":" + self._port,
                                   options=[('grpc.max_send_message_length', 30 * 1024 * 1024),
                                            ('grpc.max_receive_message_length', 30 * 1024 * 1024)]
                                   ) as channel:
            _stub = stock_pb2_grpc.StockInfStub(channel)
            _stock_code = json.dumps(code)
            _response = _stub.get_subcompany(stock_pb2.Request(stock_code = _stock_code))
            _status = _response.status
            if _status.code != 0:
                sd.log_error("get_subcompany return error:" + _status.msg)
                return None
            _list = json.loads(_response.txt)
            if type(code) == str or len(code) == 1:
                _obj = SubcompanyInfoObj(_list[0])
                return _obj
            else:
                _dct_list = []
                for _dct in _list:
                    _dct_list.append(SubcompanyInfoObj(_dct))
                return _dct_list

#6
    @sd.catch_raise_exception
    def get_industry_concept(self, code):
        with grpc.insecure_channel(self._host + ":" + self._port,
                                   options=[('grpc.max_send_message_length', 30 * 1024 * 1024),
                                            ('grpc.max_receive_message_length', 30 * 1024 * 1024)]
                                   ) as channel:
            _stub = stock_pb2_grpc.StockInfStub(channel)
            _stock_code = json.dumps(code)
            _response = _stub.get_industry_concept(stock_pb2.Request(stock_code = _stock_code))
            _status = _response.status
            if _status.code != 0:
                sd.log_error("get_industry_concept return error:" + _status.msg)
                return None
            _list = json.loads(_response.txt)
            # print(_list)
            if type(code)==str or len(code) == 1:
                _obj = IndustryConceptObj(_list[0])
                return _obj
            else:
                _dct_list = []
                for _dct in _list:
                    _dct_list.append(IndustryConceptObj(_dct))
                return _dct_list

#7
    @sd.catch_raise_exception
    def get_chairman_supervisor(self, *args):
        with grpc.insecure_channel(self._host + ":" + self._port,
                                   options=[('grpc.max_send_message_length', 30 * 1024 * 1024),
                                            ('grpc.max_receive_message_length', 30 * 1024 * 1024)]
                                   ) as channel:
            _stub = stock_pb2_grpc.StockInfStub(channel)
            if len(args) == 2:
                _response = _stub.get_chairman_supervisor(
                    stock_pb2.Request(var_num=len(args), stock_code=args[0], post=args[1]))
            else:
                _response = _stub.get_chairman_supervisor(
                    stock_pb2.Request(var_num=len(args), stock_code=args[0]))
            _status = _response.status
            if _status.code != 0:
                sd.log_error("get_chairman_supervisor return error:" + _status.msg)
                return None
            _list = json.loads(_response.txt)
            # print(_list)
            if None:
                _obj = ChairmanSupervisorObj(_list[0])
                return _obj
            _dct_list = []
            for _dct in _list:
                _dct_list.append(ChairmanSupervisorObj(_dct))
            return _dct_list

#8
    @sd.catch_raise_exception
    def get_stockholder(self, code):
        with grpc.insecure_channel(self._host + ":" + self._port,
                                   options=[('grpc.max_send_message_length', 30 * 1024 * 1024),
                                            ('grpc.max_receive_message_length', 30 * 1024 * 1024)]
                                   ) as channel:
            _stub = stock_pb2_grpc.StockInfStub(channel)
            _response = _stub.get_stockholder(stock_pb2.Request(stock_code=code))
            _status = _response.status
            if _status.code != 0:
                sd.log_error("get_stockholder return error:" + _status.msg)
                return None
            _list = json.loads(_response.txt)
            if None:
                _obj = StockHolderObj(_list[0])
                return _obj
            _dct_list = []
            for _dct in _list:
                _dct_list.append(StockHolderObj(_dct))
            return _dct_list

#9
    @sd.catch_raise_exception
    def get_trade_date(self):
        with grpc.insecure_channel(self._host + ":" + self._port) as channel:
            _stub = stock_pb2_grpc.StockInfStub(channel)
            _date_time_now = datetime.datetime.now()
            _time_str = _date_time_now.strftime("%Y-%m-%d")
            _response = _stub.get_trade_date(stock_pb2.Request(time_str=_time_str))
            _status = _response.status
            if _status.code != 0:
                sd.log_error("get_trade_date return error:" + _status.msg)
                return None
            else:
                _time_str = json.loads(_response.trade_date) + ' 03:00:00'
                # print(_time_str)
                _time = datetime.datetime.strptime(_time_str, "%Y-%m-%d %H:%M:%S")
                _result = round(_time.timestamp())
                return _result

#10
    @sd.catch_raise_exception
    def get_market_rise_fall(self):
        with grpc.insecure_channel(self._host + ":" + self._port) as channel:
            _stub = stock_pb2_grpc.StockInfStub(channel)
            _response = _stub.get_market_rise_fall(stock_pb2.Request())
            _status = _response.status
            if _status.code != 0:
                sd.log_error("get_market_rise_fall return error:" + _status.msg)
                return None
            _list = json.loads(_response.txt)
            if None:
                _obj = MarketDataObj(_list[0])
                return _obj
            _dct_list = []
            for _dct in _list:
                _dct_list.append(MarketDataObj(_dct))
            return _dct_list

#11
    @sd.catch_raise_exception
    def get_industry_rise_fall(self):
        with grpc.insecure_channel(self._host + ":" + self._port) as channel:
            _stub = stock_pb2_grpc.StockInfStub(channel)
            _response = _stub.get_industry_rise_fall(stock_pb2.Request())
            _status = _response.status
            if _status.code != 0:
                sd.log_error("get_industry_rise_fall return error:" + _status.msg)
                return None
            _list = json.loads(_response.txt)
            if None:
                _obj = IndustryDataObj(_list[0])
                return _obj
            _dct_list = []
            for _dct in _list:
                _dct_list.append(IndustryDataObj(_dct))
            return _dct_list


#12
    @sd.catch_raise_exception
    def get_concept_rise_fall(self):
        with grpc.insecure_channel(self._host + ":" + self._port) as channel:
            _stub = stock_pb2_grpc.StockInfStub(channel)
            _response = _stub.get_concept_rise_fall(stock_pb2.Request())
            _status = _response.status
            if _status.code != 0:
                sd.log_error("get_concept_rise_fall return error:" + _status.msg)
                return None
            _list = json.loads(_response.txt)
            if None:
                _obj = ConceptDataObj(_list[0])
                return _obj
            _dct_list = []
            for _dct in _list:
                _dct_list.append(ConceptDataObj(_dct))
            return _dct_list


if __name__ == '__main__':
    pass
    sesd = SenseDataService()
    # company_code = '10002320'
    stock_code = '000628'
    # stock_code = []
    # stock_code = ['300144']
    # stock_code = ['300144', '300167']
    # xw = sesd.get_stock_price_tick(stock_code) ##调试成功
    # xw = sesd.get_company_info(stock_code) ##调试成功

    # xw = sesd.get_stock_price_day(stock_code)  ##调试成功
    # xw = sesd.get_company_alias(stock_code)
    # print(datetime.datetime.utcfromtimestamp(_time).strftime("%Y-%m-%d"))
    xw = sesd.get_chairman_supervisor(stock_code)
    # print(len(xw))
    print(xw)
    # print(type(xw['水泥建材']))
    # print(xw['中小板']['stock_rise_fall'])
    #
    # print(type(xw['中小板']['stock_rise_fall']))
    # for i in xw:
    #     print(i)
    # print(xw[0], '\n')
    # print(xw[0])
    # for key in xw[0].keys():
    #     print('self.{}'.format(key) + ' = ' 'dct[' + "'" + key + "']")





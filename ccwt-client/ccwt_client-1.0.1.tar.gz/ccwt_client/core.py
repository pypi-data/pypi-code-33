#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Date    : 2018/10/27 15:31    @Author  : xycfree
# @Descript: 


import json
import os
import tempfile
import requests_cache
from ccwt_client import logger

log = logger.getLogger("core")

class CcwtClient(object):
    _session = None
    __DEFAULT_BASE_URL = 'http://210.146.174.64:8003/api/'
    __DEFAULT_TIMEOUT = 90
    __TEMPDIR_CACHE = True

    def __init__(self, base_url=__DEFAULT_BASE_URL, request_timeout=__DEFAULT_TIMEOUT, tempdir_cache=__TEMPDIR_CACHE):
        self.base_url = base_url
        self.request_timeout = request_timeout
        self.cache_filename = 'ccwt_cache'
        self.cache_name = os.path.join(tempfile.gettempdir(),
                                       self.cache_filename) if tempdir_cache else self.cache_filename

    @property
    def session(self):
        if not self._session:
            self._session = requests_cache.core.CachedSession(
                cache_name=self.cache_name, backend='sqlite',
                expire_after=60*10)

            self._session.headers.update({'Content-Type': 'application/json'})
            self._session.headers.update(
                {
                    'User-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/69.0.3497.100 Safari/537.36'}
            )
        return self._session

    def __request(self, endpoint, params):
        response_object = self.session.get(self.base_url + endpoint, params=params, timeout=self.request_timeout)
        try:
            response = json.loads(response_object.text)
            if isinstance(response, list) and response_object.status_code == 200:
                response = [dict(item, **{u'cached': response_object.from_cache}) for item in response]

            if isinstance(response, dict) and response_object.status_code == 200:
                response[u'cached'] = response_object.from_cache
        except Exception as e:
            return e
        return response

    def kline(self, **kwargs):
        """ kline params
            example:
            params = {
                'exchange': "binance", 'symbol': 'ADABTC', 'trade_date': '2018-09-18', 'start_date': '',
                'end_date': '', 'time_frame': '1m', 'limit': '10' }
        """
        response = self.__request('kline/', params=kwargs)
        return response

    def ticker(self, **kwargs):
        """ ticker params
            example:
            params = {
                'exchange': "binance", 'symbol': 'ADABTC', 'trade_date': '2018-09-18', 'start_date': '',
                'end_date': '', 'time_frame': '1m', 'limit': '10' }
        """
        response = self.__request('ticker/', params=kwargs)
        return response

    def depth(self, **kwargs):
        """ depth params
            example:
            params = {
                'exchange': "binance", 'symbol': 'ADABTC', 'trade_date': '2018-09-18', 'start_date': '',
                'end_date': '', 'time_frame': '1m', 'limit': '10' }
        """
        response = self.__request('depth/', params=kwargs)
        return response

    def order(self, **kwargs):
        """ order params
            example:
            params = {
                'exchange': "binance", 'symbol': 'ADABTC', 'trade_date': '2018-09-18', 'start_date': '',
                'end_date': '', 'time_frame': '1m', 'limit': '10' }
        """
        response = self.__request('order/', params=kwargs)
        return response

    def trade(self, **kwargs):
        """ trade params
            example:
            params = {
                'exchange': "binance", 'symbol': 'ADABTC', 'trade_date': '2018-09-18', 'start_date': '',
                'end_date': '', 'time_frame': '1m', 'limit': '10' }
        """
        response = self.__request('trade/', params=kwargs)
        return response

    def index(self, **kwargs):
        response = self.__request('/', params=kwargs)
        return response

    def future_index(self, **kwargs):
        response = self.__request('future/index', params=kwargs)
        return response

    def future_kline_or_ticker(self, **kwargs):
        response = self.__request('future/kline_ticker', params=kwargs)
        return response

    def future_week_kline_ticker(self, **kwargs):
        response = self.__request('future/week/kline_ticker', params=kwargs)
        return response

    def future_next_week_kline_ticker(self, **kwargs):
        response = self.__request('future/next_week/kline_ticker', params=kwargs)
        return response

    def future_quarter_kline_ticker(self, **kwargs):
        response = self.__request('future/quarter/kline_ticker', params=kwargs)
        return response




cli = CcwtClient()

if __name__ == '__main__':
    # params = {
    #     'exchange': "bitmex", 'symbol': 'XBTUSD', 'trade_date': '2018-09-18', 'start_date': '',
    #     'end_date': '', 'time_frame': '1m', 'limit': '10'
    # }
    instrument = 'bitmex_XBTUSD'
    params = {
        'exchange': instrument.split('_')[0], 'symbol': instrument.split('_')[-1], 'start_date': '',
        'end_date': ''
    }
    cc = CcwtClient()
    res = cc.kline(**params)
    print(type(res))
    print(res)

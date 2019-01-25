#!/usr/bin/python
# -*- coding:utf-8 -*-

"""
    @file:      http_client.py
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    @auther:    tangmi(tangmi360@gmail.com)
    @date:      June 11, 2018
    @desc:      Basic http client functions
"""

from aiohttp import ClientSession


class HttpClient(ClientSession):
    def __init__(self, *args, **kwargs):
        super(HttpClient, self).__init__(*args, **kwargs)

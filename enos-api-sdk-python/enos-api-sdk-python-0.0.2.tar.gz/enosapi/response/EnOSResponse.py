# coding: utf8
# Author:xuyang.li
# Date:2018/11/20
"""
    EnOS response
"""


class EnOSResponse:
    def __init__(self, status, request_id, submsg, body, data, msg):
        self.status = status
        self.request_id = request_id
        self.submsg = submsg
        self.body = body
        self.data = data
        self.msg = msg

    def is_success(self):
        return self.status == 0

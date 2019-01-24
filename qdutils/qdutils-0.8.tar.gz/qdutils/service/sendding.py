#  -*- coding: utf-8 -*-

'''

@desc: 
@author: tony
@Date: 2018/12/26 下午7:07

'''
import json
from qdutils.common.stringutils import stringutils
from qdutils.common.httputils import httputils


class sendding(object):
    pass

    @staticmethod
    def send_ding(url, content, isAtAll=False):
        """
        发送钉钉消息
        :param url: 机器人url
        :param content: 发送内容 
        :param isAtAll: 是否@所有人 
        :return: 
        """
        flag = True
        if stringutils.not_empty(url) and stringutils.not_empty(content):
            json_rs = sendding.get_ding_json(content, isAtAll)
            flag, result = httputils.http_post(url, json_rs)
        return flag

    @staticmethod
    def get_ding_json(content, isAtAll=False, atMobiles=None):
        json_rs = ''
        json_dict = {}
        json_dict['msgtype'] = 'text'
        content_dict = {}
        content_dict['content'] = content
        json_dict['text'] = json.loads(json.dumps(content_dict, ensure_ascii=False, encoding='UTF-8'))
        at_dict = {}
        if not stringutils.strIsEmpty(atMobiles):
            mobile_list = atMobiles.split(',')
            at_dict['atMobiles'] = json.loads(json.dumps(mobile_list, ensure_ascii=False, encoding='UTF-8'))
        at_dict['isAtAll'] = isAtAll
        json_dict['at'] = json.loads(json.dumps(at_dict, ensure_ascii=False, encoding='UTF-8'))
        json_rs = json.dumps(json_dict, ensure_ascii=False, encoding='UTF-8')
        return str(json_rs)

# -*- coding: utf-8 -*-

try:
    from urllib.parse import urljoin
except ImportError:
    from urlparse import urljoin
import requests
import json
from tpspy.base import ClientBase


class ClientMessage(ClientBase):
    class MessageChannel(object):
        # 企业微信-群聊-文本
        WECHAT_WORK_GROUP_CHAT_TEXT = "WECHAT_WORK_GROUP_CHAT_TEXT"
        # 企业微信-群聊-图文
        WECHAT_WORK_GROUP_CHAT_NEWS = "WECHAT_WORK_GROUP_CHAT_NEWS"
        # 企业微信-群聊-卡片
        WECHAT_WORK_GROUP_CHAT_CARD = "WECHAT_WORK_GROUP_CHAT_CARD"
        # 企业微信-应用推送-文本
        WECHAT_WORK_APP_PUSH_TEXT = "WECHAT_WORK_APP_PUSH_TEXT"
        # 企业微信-应用推送-图文
        WECHAT_WORK_APP_PUSH_NEWS = "WECHAT_WORK_APP_PUSH_NEWS"
        # 企业微信-应用推送-卡片
        WECHAT_WORK_APP_PUSH_CARD = "WECHAT_WORK_APP_PUSH_CARD"
        # 企业微信-群聊机器人
        WECHAT_WORK_GROUP_ROBOT_TEXT = "WECHAT_WORK_GROUP_ROBOT_TEXT"
        # 企业微信-群聊机器人
        WECHAT_WORK_GROUP_ROBOT_MD = "WECHAT_WORK_GROUP_ROBOT_MD"

        # 微信推送
        WECHAT = "WECHAT"

        # 邮件, 内部邮件(包括外部邮件)
        MAIL = "MAIL"

        # 邮件, 仅外部邮件
        MAIL_OUTER = "MAIL_OUTER"

        # 短信
        SMS = "SMS"

    def __init__(self, sys_id=None, sys_secret=None, tps_base_url=None):
        super(ClientMessage, self).__init__(sys_id=sys_id, sys_secret=sys_secret, tps_base_url=tps_base_url)

    def message_send(self, msg_type, to, content):
        url = urljoin(self.tps_base_url, "api/v1/message/send")
        import json
        print(json.dumps(dict(
            type=msg_type,
            to=to,
            content=content,
        )))
        resp = requests.get(url, json=dict(
            type=msg_type,
            to=to,
            content=content,
        ), headers=self.auth_headers)
        try:
            v = resp.json()
        except Exception as e:
            print("resp: %s" % resp.text)
            raise e
        return v

    def message_chat_create(self, name, owner, user_list):
        url = urljoin(self.tps_base_url, "api/v1/message/chat")
        print(json.dumps(dict(
            name=name,
            owner=owner,
            user_list=user_list,
        )))
        resp = requests.post(url, json=dict(
            name=name,
            owner=owner,
            user_list=user_list,
        ), headers=self.auth_headers)
        return resp.json()

    def message_chat_info(self, chat_id=''):
        url = urljoin(self.tps_base_url, "api/v1/message/chat")
        print(json.dumps(dict(
            chat_id=chat_id
        )))
        resp = requests.get(url, json=dict(
            chat_id=chat_id
        ), headers=self.auth_headers)
        return resp.json()

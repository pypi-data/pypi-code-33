# -*- coding: utf-8 -*-


import os
import time
from tpspy.client import Client

TPS_SYS_ID = os.getenv("TPS_SYS_ID", '')
TPS_SYS_SECRET = os.getenv("TPS_SYS_SECRET", '')

client = Client(sys_id=TPS_SYS_ID, sys_secret=TPS_SYS_SECRET, tps_base_url="http://127.0.0.1:30180/")
# client = Client(sys_id=TPS_SYS_ID, sys_secret=TPS_SYS_SECRET, tps_base_url="https://tencent.qq.com/")
# client = Client(sys_id=TPS_SYS_ID, sys_secret=TPS_SYS_SECRET, tps_base_url="https://test.tencent.qq.com/")


def test_api():
    r = client.api_tapd_tencent(method="GET", path="bugs.json", params={
        "workspace_id": 10066461,
        "title": "QAPM"
    })
    print(r)
    assert isinstance(r, dict) and r.get("code") == 10000


def test_message():
    to = ["1356761908@qq.com", "soonflywang"]
    to_outer = "1356761908@qq.com"
    to_chat = '13294344628055079709'
    to_key = '489b78c9-1769-49c5-ae6e-6aff219429d6'  # webhook
    content = dict(
        title="快递到达通知",
        body="\n # Hi, 您的快递到了 ! <h1>这是H1<h1>",
        pic_url="https://p.qpic.cn/pic_wework/3685288192/c8cedbc46b2c0d0b3e67f273eace5834d49e2dec5885fd8b/0",
        detail_url="https://work.weixin.qq.com/api/doc#90000/90135/90248"
    )

    # user
    # r = client.message_send(msg_type=client.MessageChannel.WECHAT, to=to, content=content)
    # print("WECHAT, ", r)
    #
    # r = client.message_send(msg_type=client.MessageChannel.WECHAT_WORK_APP_PUSH_TEXT, to=to, content=content)
    # print("WECHAT_WORK_APP_PUSH_TEXT, ", r)
    #
    # r = client.message_send(msg_type=client.MessageChannel.WECHAT_WORK_APP_PUSH_NEWS, to=to, content=content)
    # print("WECHAT_WORK_APP_PUSH_NEWS, ", r)
    #
    r = client.message_send(msg_type=client.MessageChannel.MAIL, to=to, content=content)
    print("MAIL, ", r)

    # r = client.message_send(msg_type="MAIL_OUTER", to=to_outer, content=content)
    # print("MAIL_OUTER, , ", r)

    # r = client.message_send(msg_type=client.MessageChannel.MAIL_OUTER, to=to, content=content)
    # print("MAIL_OUTER, but send inner, should be error", r)

    # r = client.message_send(msg_type=client.MessageChannel.SMS, to=to, content=content)
    # print("SMS, ", r)

    # r = client.message_send(msg_type=client.MessageChannel.WECHAT_WORK_APP_PUSH_TEXT, to=to, content=content)
    # print("WECHAT_WORK_APP_PUSH_TEXT, ", r)
    #
    # r = client.message_send(msg_type=client.MessageChannel.WECHAT_WORK_APP_PUSH_CARD, to=to, content=content)
    # print("WECHAT_WORK_APP_PUSH_CARD, ", r)

    # web hook
    # r = client.message_send(msg_type=client.MessageChannel.WECHAT_WORK_GROUP_ROBOT_TEXT, to=to_key, content=content)
    # print("WECHAT_WORK_GROUP_ROBOT_TEXT, ", r)
    #
    # r = client.message_send(msg_type=client.MessageChannel.WECHAT_WORK_GROUP_ROBOT_MD, to=to_key, content=content)
    # print("WECHAT_WORK_GROUP_ROBOT_MD, ", r)

    # chat
    # r = client.message_send(msg_type=client.MessageChannel.WECHAT_WORK_GROUP_CHAT_TEXT, to=to_chat, content=content)
    # print("WECHAT_WORK_GROUP_CHAT_TEXT, ", r)
    #
    # r = client.message_send(msg_type=client.MessageChannel.WECHAT_WORK_GROUP_CHAT_CARD, to=to_chat, content=content)
    # print("WECHAT_WORK_GROUP_CHAT_CARD, ", r)
    #
    # r = client.message_send(msg_type=client.MessageChannel.WECHAT_WORK_GROUP_CHAT_NEWS, to=to_chat, content=content)
    # print("WECHAT_WORK_GROUP_CHAT_NEWS, ", r)

    # multi
    # msg_types = ",".join([
    # client.MessageChannel.WECHAT,
    # client.MessageChannel.MAIL,
    # client.MessageChannel.WECHAT_WORK_APP_PUSH_TEXT])
    # r = client.message_send(msg_type=msg_types, to=to, content=content)
    # print("MULTICHANNEL MSG, ", r)

    # r = client.message_chat_create("test", "soonflywang", "soonflywang;kangtian")
    # print("MESSAGE_CHAT_CREATE ", r)
    #
    # r = client.message_chat_info(chat_id=to_chat)
    # print("MESSAGE_CHAT_INFO", r)


def test_metrics_resource_flow_upload():
    resp = client.metrics_resource_flow_upload(data=[
        {
            "time_start": float(time.time()),
            "time_end": float(time.time()) + 5,
            "namespace": "athena",
            "resource": "uba.ui_action",
            "stage": "entrance_init",
            "state": "ok",
            "value": 1,

        },
    ])
    print("resp.text: ", resp)


def test_metrics_resource_flow_get():
    resp = client.metrics_resource_flow_get(params={
        "filter": {"stage": "entrance.init"}
    })
    print("resp.text: ", resp)

if __name__ == "__main__":
    # test_api()
    test_message()
    # test_metrics_resource_flow_upload()
    # test_metrics_resource_flow_get()

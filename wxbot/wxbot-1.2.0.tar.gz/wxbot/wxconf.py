# -*- coding:utf-8 -*-


class WXConf:
    def __init__(self):

        # 基本配置
        self.baseconf = {
            # 调试模式
            'debug' : True,
            # WXBot 掉线后自动重启
            "restartOnOffline": False,
            # 是否记录日志
            'log' : True,
            # 日志文件存放位置
            'logPath' : 'D:/Users/Administrator/PycharmProjects/wxbot/log/',
            # 登录二维码保存类型 bytes
            'qrCodeType': 'bytes',
            # 登录二维码保存位置，仅当保存类型为file时启用
            'qrCodePath': 'D:/Users/Administrator/PycharmProjects/wxbot/log/',
            'version': "v1.2.0",
            'help': """
[wxbot]
    启动服务：wxbot
    选项：
        -v, --version    显示版本信息
        -h, --help       帮助信息
        -r, --restart    重新登录
        -s, --stop       停止服务
[wx]
    更新：
        update group     更新群组
        update buddy     更新联系人
    查询：
        list group       查询群组
        list buddy       查询联系人
    发送：
        send group xxx xxx   发送群组消息
        send buddy xxx xxx   发送好友消息
"""
        }

        # 邮件配置
        self.mailconf = {
            # 邮件服务器地址
            'mailServerAddr': 'smtp.qq.com',
            # 邮件服务器端口
            'mailServerPort': '465',
            # 邮件服务器密码
            'mailServerPswd': 'xxxxxxxxxxxxxxx',
            # 发送地址
            'fromUser': 'xxxxxxxxxxxxxxx',
            #  接收二维码邮件地址
            'toUser': 'xxxxxxxxxxxxxx',
        }


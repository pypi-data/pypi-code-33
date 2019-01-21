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
            'qrCodePath': 'D:/Users/Administrator/PycharmProjects/wxbot/log/'
        }

        # 邮件配置
        self.mailconf = {
            # 邮件服务器地址
            'mailServerAddr': 'smtp.qq.com',
            # 邮件服务器端口
            'mailServerPort': '465',
            # 邮件服务器密码
            'mailServerPswd': 'zzobqxdahxgzdhid',
            # 发送地址
            'fromUser': 'cfn@leapy.cn',
            #  接收二维码邮件地址
            'toUser': '2565275061@qq.com',
        }


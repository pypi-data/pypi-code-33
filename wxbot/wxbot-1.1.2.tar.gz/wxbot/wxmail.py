# -*- coding:utf-8 -*-
__authon__ = "cfn@leapy.cn"

from wxbot import wxconf
from wxbot import wxmessage
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.image import MIMEImage

class MyMail(wxmessage.message):
    def __init__(self, data):
        wxmessage.message.__init__(self)
        self.serverAddr = wxconf.WXConf().mailconf['mailServerAddr']
        self.serverport = wxconf.WXConf().mailconf['mailServerPort']
        self.serverpswd = wxconf.WXConf().mailconf['mailServerPswd']
        self.fromUser = wxconf.WXConf().mailconf['fromUser']
        self.toUser = wxconf.WXConf().mailconf['toUser']
        self.qrCodeType = wxconf.WXConf().baseconf['qrCodeType']
        self.data = data
        # print(self.data['content'])
        pass

    # 发送邮件
    def sendMail(self):
        s = SMTP(self.serverAddr, self.serverport, self.serverpswd, self.fromUser, self.toUser)
        if 'content' in self.data:
            s.add_Content(self.data['content'], 'plain')
        if 'image' in self.data:
            s.add_img(self.data['image'],self.qrCodeType)
        s.send()

        pass

    def run(self):
        self.sendMail()
        pass


# 发送邮件
class SMTP(wxmessage.message):
    def __init__(self, serverAddr,serverport,serverpswd,fromUser, toUser):
        wxmessage.message.__init__(self)
        self.serverAddr = serverAddr
        self.serverport = serverport
        self.serverpswd = serverpswd
        self.fromUser,self.toUser = fromUser,toUser
        self.init()

    # 初始化
    def init(self):
        self.msg = MIMEMultipart()
        # 邮件主题
        self.msg['Subject'] = 'WXbot微信登录邮件'
        # 谁发送
        self.msg['From'] = self.fromUser
        # 发送谁
        self.msg['To'] = self.toUser
        pass

    # 正文
    # type 可以是 html plain
    def add_Content(self,data,type):
        # 创建正文
        if data:
            self.msg.attach(MIMEText(data, type, 'utf-8'))
        pass

    # 添加图片
    def add_img(self, img,img_type='file'):
        if img_type == 'file':
            img_file = open(img, 'rb').read()
            msg_img = MIMEImage(img_file)
            msg_img.add_header('Content-Disposition', 'attachment', filename='qrcode.jpg')
            self.msg.attach(msg_img)
        elif img_type == 'bytes':
            msg_img = MIMEImage(img)
            msg_img.add_header('Content-Disposition', 'attachment', filename='qrcode.jpg')
            self.msg.attach(msg_img)
        pass

    # 发送邮件
    def send(self):
        try:
            s = smtplib.SMTP_SSL(self.serverAddr, self.serverport)
            s.set_debuglevel(self.debug)  # 输出发送邮件详细过程
            s.login(self.fromUser, self.serverpswd)
            s.sendmail(self.fromUser, self.toUser, self.msg.as_string())
            self.success('发送邮件成功')

        except Exception as e:
            self.error('发送邮件失败:', e)

if __name__ == '__main__':
    data = {
        'content': '请使用微信扫码登录邮件中的二维码'
    }
    MyMail(data).run()



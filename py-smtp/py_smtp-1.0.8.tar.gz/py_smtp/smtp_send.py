#!/usr/bin/env python
# -*- coding: utf-8 -*-
__title__ = ''
__author__ = 'HaiFeng'
__mtime__ = ''

from email.mime.image import MIMEImage
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email.utils import formataddr
import email
import smtplib
import os.path
import mimetypes


def make_html_msg(content: str):
    """一个包含文本和html的多部分邮件。多部分消息通常包含纯文本和html格式，客户端自行选择显示哪个。（web客户端显示html，命令行客户端显示纯文本）"""
    myemail = MIMEMultipart('alternative')
    html = MIMEText(content, 'html', _charset="utf-8")
    myemail.attach(html)  # 消息正文绑定到邮件对象
    return myemail

def make_txt_msg(content: str):
    """一个包含文本和html的多部分邮件。多部分消息通常包含纯文本和html格式，客户端自行选择显示哪个。（web客户端显示html，命令行客户端显示纯文本）"""
    myemail = MIMEMultipart('alternative')
    text = MIMEText(content, 'plain', _charset="utf-8")  # 纯文本的邮件消息正文
    myemail.attach(text)  # 消息正文绑定到邮件对象
    # html = MIMEText(  # html邮件消息正文
    #     '<html><body><h4>Hello World!</h4>'
    #     '</body></html>', 'html')
    # myemail.attach(html)  # 消息正文绑定到邮件对象
    return myemail


def make_img_msg(imgfile):
    """创建一个文本和图片的邮件"""
    f = open(imgfile, 'rb')  # 创建文件指针,这里要以rb的模式取读
    data = f.read()  # 读取图片成字节流
    f.close()  # 文件关闭
    ctype, encoding = mimetypes.guess_type(imgfile)  # ctype为根据文件获取的数据传输类型image/jpeg，encoding应该为None
    if ctype is None or encoding is not None:
        ctype = 'application/octet-stream'
    maintype, subtype = ctype.split('/', 1)  # maintype为文件所属类image，subtype为具体文件类型jpeg
    myemail = MIMEImage(data, name=subtype)  # 生成图片邮件,name=文件类型jpeg
    email.encoders.encode_base64(myemail)  # 将邮件编码
    # 设置附件头
    basename = os.path.basename(file_name)  # basename为文件名，不包含路径
    myemail.add_header('Content-Disposition', 'attachment', filename=('gbk', '', basename))  # 添加邮件头
    return myemail


def make_file_msg(file_names: []):
    """创建一个文本和文件的邮件"""
    msg = MIMEMultipart()
    for file_name in file_names:
        # 构造MIMEBase对象做为文件附件内容并附加到根容器
        ctype, encoding = mimetypes.guess_type(file_name)  # ctype为根据文件获取的数据传输类型image/jpeg，encoding应该为None
        if ctype is None or encoding is not None:
            ctype = 'application/octet-stream'
        maintype, subtype = ctype.split('/', 1)  # maintype为文件所属类image，subtype为具体文件类型jpeg
        print(maintype, subtype)
        # 读入文件内容并格式化
        f = open(file_name, 'rb')  # 创建文件指针,这里要以rb的模式取读
        myemail = MIMEBase(maintype, subtype)
        myemail.set_payload(f.read())  # 设置负载数据
        f.close()
        email.encoders.encode_base64(myemail)  # 将邮件编码
        # 设置附件头
        basename = os.path.basename(file_name)  # basename为文件名，不包含路径
        myemail.add_header('Content-Disposition', 'attachment', filename=('gbk', '', basename))  # 添加邮件头
        msg.attach(myemail)
    return msg


def send(host, port, sender, pwd: str, to: [], cc: [], subject: str, content: str, attach_files: []) -> []:
    """
    邮件发送
        :param host: 服务器,smtp.263.net:465
        :param sender: ['呢称', 'xxx@mmm.com.cn'] or 'xxx@mmm.com.cn'
        :param pwd:str: 密码 or 密钥
        :param to:[]: 收件人列表
        :param cc:[]: 抄送人列表
        :param subject:str: 标题
        :param content:str: 邮件内容
        :param attach_files:[]: 附件列表
    return [是否成功, 错误说明]
    """
    msg = make_file_msg(attach_files)
    if type(sender) is list:
        msg['From'] = formataddr(sender)
    else:
        msg['From'] = sender
    msg['To'] = ', '.join(to)
    msg['Cc'] = ','.join(cc)
    msg['Subject'] = subject
    if '<html>' in content.lower():
        msg.attach(make_html_msg(content))
    else:
        msg.attach(make_txt_msg(content))

    sendSvr = smtplib.SMTP_SSL(host, port)  # .SMTP()
    # sendSvr.connect(host)  # 连接服务器
    fr_mail = sender if type(sender) is str else sender[-1]
    sendSvr.login(fr_mail, pwd)  # 登录操作
    sendSvr.sendmail(fr_mail, to, msg.as_string())  # 参数：发件人，收件人，消息正文
    sendSvr.quit()


if __name__ == '__main__':
    # dir_path = os.path.dirname(os.path.abspath(__file__))
    send('smtp服务器:端口', ['测试员', 'wujh@ebfcn.com.cn'], '密码', ['收件人1', '收件人2'], ['抄送人1', '抄送人2'], '标题', '内容', ['附件1', '附件2'])

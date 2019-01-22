
# coding: utf-8

import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.header import Header
from qbase.common import configer as cf


def sendMail(subject, text, attach_file=''):
    conf = cf.configer()
    # 设置smtplib所需的参数
    # 下面的发件人，收件人是用于邮件传输的。
    smtpserver = conf.getValueByKey("email", "smtpserver")
    sender = conf.getValueByKey("email", "sender")
    password = conf.getValueByKey("email", "password")
    receiver = eval(conf.getValueByKey("email", "receivers"))
    msg = MIMEMultipart('mixed')
    msg.attach(MIMEText(text, 'plain', 'utf-8'))
    if attach_file:
        with open(attach_file, 'rb') as f:
            # 设置附件的MIME和文件名，这里是png类型:
            text_att = MIMEText(f.read(), 'base64', 'utf-8')
            text_att["Content-Type"] = 'application/octet-stream'
            file = attach_file.split('\\')[-1]
            text_att.add_header('Content-Disposition', 'attachment', filename=('gbk', '', file))
            msg.attach(text_att)
    msg['Subject'] = Header(subject, 'utf-8')
    msg['from'] = sender
    msg['to'] = ';'.join(receiver)
    server = smtplib.SMTP_SSL()  # server = smtplib.SMTP()

    # server.set_debuglevel(1)

    server.connect(smtpserver, 465)

    # server = smtplib.SMTP_SSL(smtp_server,465)

    server.ehlo(smtpserver)

    server.login(sender, password)

    server.sendmail(sender, receiver, msg.as_string())

    server.quit()

    print('email has send out !')

    return True



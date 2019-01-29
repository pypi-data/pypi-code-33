import smtplib
from email.mime.application import MIMEApplication
from email.mime.image import MIMEImage
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from performance import TODAY, DEBUG, config


def send_mail(report):
    assert isinstance(report, Report)
    # 设置smtplib所需的参数
    # 下面的发件人，收件人是用于邮件传输的。
    smtpserver = config.smtp_server
    username = config.user_name
    password = config.password
    sender = config.sender
    # 收件人为多个收件人
    receiver = config.mail_to

    cc = config.cc

    subject = '%s内存检查报告(%s)' % (report.pkg, TODAY)
    # 通过Header对象编码的文本，包含utf-8编码信息和Base64编码信息。以下中文名测试ok
    # subject = '中文标题'
    # subject=Header(subject, 'utf-8').encode()

    # 构造邮件对象MIMEMultipart对象
    # 下面的主题，发件人，收件人，日期是显示在邮件页面上的。
    msg = MIMEMultipart('mixed')
    msg['Subject'] = subject
    msg['From'] = 'PTK<qinchao@aicaigroup.com>'
    # msg['To'] = 'XXX@126.com'
    # 收件人为多个收件人,通过join将列表转换为以;为间隔的字符串
    msg['To'] = ";".join(receiver)
    msg['Cc'] = ";".join(cc)
    # msg['Date']='2012-3-16'

    # 构造文字内容
    text = """
        <html>
        <head>
        <meta charset="utf-8" />
        </head>
        <body>
        <p>
            <div>内存摘要(%s)信息如下：<br/>
            查看详情请登录到172.16.14.201服务器,检查报告在目录/Users/chooseway/ptk/</div>
        <p>
            <div><b>执行成功:</b> %s</div>
            <div><b>执行时长:</b> %.1f小时</div>
            <div><b>应用名称:</b> %s<br/></div>
            <div><b>检测设备:</b> %s<br/></div>
            <p>
            <div><b>ANR 数量:</b> %d</div>
            <div><b>App Crash数量:</b> %d</div>

            <p></p>
            <div><b>内存最大值:</b> %s(KB)</div>
            <div><b>内存平均值:</b> %s(KB)</div>

            <p></p>
            <div><b>内存变化曲线:</b></div>
            <img src="cid:plt_simple"/>
            <div><b>历史最大、平均内存:</b><div>
            <img src="cid:plt_history_simple"/>
        </body>
        </html>
    """ % (TODAY, report.success, report.duration, report.pkg, report.device,
           len(report.anrs), len(report.crashes), report.max, report.avg)

    plt_simple = open(report.plt_simple, 'rb').read()
    plt_simple_image = MIMEImage(plt_simple)
    plt_simple_image.add_header('Content-ID', '<plt_simple>')
    msg.attach(plt_simple_image)

    plt_history = open(report.plt_history, 'rb').read()
    plt_history_image = MIMEImage(plt_history)
    plt_history_image.add_header('Content-ID', '<plt_history_simple>')
    msg.attach(plt_history_image)

    plt_simple_file = MIMEText(text, 'html', _charset="utf-8")
    msg.attach(plt_simple_file)

    # 构造附件
    for anr in report.anrs:
        anr_file = MIMEText(open(anr, 'rb').read(), 'base64', 'utf-8')
        anr_file["Content-Type"] = 'application/octet-stream'
        anr_file["Content-Disposition"] = 'attachment; filename=%s' % anr
        msg.attach(anr_file)

    for crash in report.crashes:
        crash_file = MIMEText(open(crash, 'rb').read(), 'base64', 'utf-8')
        crash_file["Content-Type"] = 'application/octet-stream'
        crash_file["Content-Disposition"] = 'attachment; filename=%s' % crash
        msg.attach(crash_file)

    xlsx_file = MIMEApplication(open(report.xlsx, 'rb').read())
    xlsx_file["Content-Type"] = 'application/octet-stream'
    xlsx_file["Content-Disposition"] = 'attachment; filename=%s' % report.xlsx
    msg.attach(xlsx_file)

    # 发送邮件
    smtp = smtplib.SMTP()
    smtp.connect(smtpserver)
    # 我们用set_debuglevel(1)就可以打印出和SMTP服务器交互的所有信息。
    smtp.set_debuglevel(1)
    smtp.login(username, password)
    smtp.sendmail(sender, receiver, msg.as_string())
    smtp.quit()
    pass


class Report:

    def __init__(self):
        self.pkg = None
        self.duration = None
        self.device = None
        self.max = None
        self.avg = None
        self.plt_simple = None
        self.xlsx = None
        self.crashes = []
        self.anrs = []
        self.plt_history = None
        self.success = True

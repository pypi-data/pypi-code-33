#  -*- coding: utf-8 -*-

'''

@desc: 
@author: tony
@Date: 2018/12/26 下午7:06

'''
import smtplib
import email
import sys
import os
import traceback
from email.mime.text import MIMEText
from email.Message import Message
from email.mime.multipart import MIMEMultipart
from email.Header import Header


class sendmail(object):
    pass

    def __init__(self, cc=''):
        pass

    def get_content_table(self, header_list, cont_list):
        """
        根据表格标题和内容获取邮件表格内容
        :param header_list: ['日报名称','今日完成时间']
        :param cont_list:  [['aa','2017-09-10'],['bb','2017-09-10']]
        :return: 
        """
        html = "<!DOCTYPE html><html lang=\"en\"><head><meta charset=\"UTF-8\"><title>Title</title></head><style type=\"text/css\">    table.gridtable {        font-family: verdana,arial,sans-serif;        font-size:11px;        color:#333333;        border-width: 1px;        border-color: #666666;        border-collapse: collapse;    }    table.gridtable th {        border-width: 1px;        padding: 8px;        border-style: solid;        border-color: #666666;        background-color: #FFA500;    }    table.gridtable td {        border-width: 1px;        padding: 8px;        border-style: solid;        border-color: #666666;        background-color: #E0FFFF;    }</style><body>"
        html = html + "<table class=\"gridtable\" >"
        header = '<tr>'
        for head in header_list:
            header = header + '<th>{}</th>'.format(head)
        header = header + '</tr>'
        html = html + header

        for one_cont_list in cont_list:
            html = html + '<tr>'
            for one_cont in one_cont_list:
                html = html + '<td>{}</td>'.format(one_cont)
            html = html + '</tr>'
        html = html + "</table></body></html>"
        return html

    def get_content_table(self, header_list, cont_list):
        """
        根据表格标题和内容获取邮件表格内容
        :param header_list: ['日报名称','今日完成时间']
        :param cont_list:  [['aa','2017-09-10'],['bb','2017-09-10']]
        :return: 
        """
        html = "<!DOCTYPE html><html lang=\"en\"><head><meta charset=\"UTF-8\"><title>Title</title></head><style type=\"text/css\">    table.gridtable {        font-family: verdana,arial,sans-serif;        font-size:11px;        color:#333333;        border-width: 1px;        border-color: #666666;        border-collapse: collapse;    }    table.gridtable th {        border-width: 1px;        padding: 8px;        border-style: solid;        border-color: #666666;        background-color: #FFA500;    }    table.gridtable td {        border-width: 1px;        padding: 8px;        border-style: solid;        border-color: #666666;        background-color: #E0FFFF;    }</style><body>"
        html = html + "<table class=\"gridtable\" >"
        header = '<tr>'
        for head in header_list:
            header = header + head
        header = header + '</tr>'
        html = html + header

        for one_cont_list in cont_list:
            html = html + '<tr>'
            for one_cont in one_cont_list:
                html = html + '<td>{}</td>'.format(one_cont)
            html = html + '</tr>'
        html = html + "</table></body></html>"
        return html

    def get_content_table2(self, header_list, cont_list):
        """
        根据表格标题和内容获取邮件表格内容
        :param header_list: 自定义header，['<th colspan="3">日报名称</th>']
        :param cont_list:  [['aa','2017-09-10'],['bb','2017-09-10']]
        :return: 
        """
        html = "<!DOCTYPE html><html lang=\"en\"><head><meta charset=\"UTF-8\"><title>Title</title></head><style type=\"text/css\">    table.gridtable {        font-family: verdana,arial,sans-serif;        font-size:11px;        color:#333333;        border-width: 1px;        border-color: #666666;        border-collapse: collapse;    }    table.gridtable th {        border-width: 1px;        padding: 8px;        border-style: solid;        border-color: #666666;        background-color: #FFA500;    }    table.gridtable td {        border-width: 1px;        padding: 8px;        border-style: solid;        border-color: #666666;        background-color: #E0FFFF;    }</style><body>"
        html = html + "<table class=\"gridtable\" >"
        header = '<tr>'
        for head in header_list:
            header = header + head
        header = header + '</tr>'
        html = html + header

        for one_cont_list in cont_list:
            html = html + '<tr>'
            for one_cont in one_cont_list:
                html = html + '<td>{}</td>'.format(one_cont)
            html = html + '</tr>'
        html = html + "</table></body></html>"
        return html

    def send_mail(self, to='', subj='', content='', attach=None):
        """
        发送邮件
        :param to:  收件人 
        :param subj:    标题
        :param content: 内容
        :param attach:  附件 
        :return: True：发送成功，False：发送失败 
        """
        flag = True
        msg = Message()
        COMMASPACE = ', '
        if not to:
            to = self.to
        to = map(self.addsuff, to)
        print to
        if not subj:
            subj = self.subj
        if not content:
            content = self.subj
        msg = MIMEMultipart()
        msg['From'] = self.emailfrom
        if self.cc:
            msg['CC'] = self.cc
        msg['To'] = COMMASPACE.join(to)
        msg['Subject'] = Header(subj, 'utf-8')
        msg['Date'] = email.Utils.formatdate()
        if not attach:
            msg.set_payload(content)
        else:
            msg.attach(content)
            msg.attach(attach)
        try:

            failed = self.server.sendmail(
                self.emailfrom, to, msg.as_string())  # may also raise exc
        except Exception, ex:
            flag = False
            print traceback.print_exc()
        return flag

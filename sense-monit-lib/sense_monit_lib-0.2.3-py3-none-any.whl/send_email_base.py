#!/usr/bin/python
# -*- coding:utf-8 -*-

from email.mime.text import MIMEText
from email.header import Header
import smtplib
import sense_core as sd


MAIL_HOST = sd.config('email','host')
MAIL_USER = sd.config('email','user')
MAIL_PASS = sd.config('email','pass')

def send_email(module,email_list,subject,context):
	receiver = email_list
	message = MIMEText(context, 'plain', 'utf-8')
	message['From'] = Header('日志监控', 'utf-8')
	message['Module'] = Header(module, 'utf-8')
	message['Subject'] = Header(subject, 'utf-8')
	try:
		smtpObj = smtplib.SMTP_SSL(MAIL_HOST,465)
		smtpObj.ehlo()
		smtpObj.login(MAIL_USER,MAIL_PASS)
		res = smtpObj.sendmail(MAIL_USER, receiver, message.as_string())
		smtpObj.close()
		return res
	except Exception as e:
		sd.log_exception(e)
		return None
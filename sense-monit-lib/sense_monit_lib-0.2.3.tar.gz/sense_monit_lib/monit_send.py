#!/usr/bin/env python
# -*- coding: utf-8 -*-
from .send_email import MonitEmialSender
from .send_message import MonitMsgSender
import datetime
from .models import *

class MonitMessageSender(object):
	
	__send_msg_dict = {}
	__send_email_dict = {}
	
	@classmethod
	def send_message(cls, module, title, phone_list=None):
		global __send_msg_dict
		_now = datetime.datetime.now()
		monitor_msg = MonitMsgSender()
		if phone_list == None:
			monitor_msg.send_message_with_db(module, title)
		else:
			if module not in cls.__send_msg_dict:
				cls.__send_msg_dict[module] = _now
				monitor_msg._send_err_message(module, title, phone_list)
			else:
				last_send_time = cls.__send_msg_dict[module]
				if last_send_time < (_now + datetime.timedelta(minutes=-20)):
					cls.__send_msg_dict[module] = _now
					monitor_msg._send_err_message(module, title, phone_list)
				else:
					sd.log_info('The module of {0} has send err message in last 20 minutes'.format(module))
					return None
	
	@classmethod
	def send_email(cls, module, title,  subject, receiver_email=None):
		global __send_email_dict
		_now = datetime.datetime.now()
		monitor_email = MonitEmialSender()
		if receiver_email == None:
			monitor_email.send_email_with_db(module, title, subject)
		else:
			if module not in cls.__send_email_dict:
				cls.__send_email_dict[module] = _now
				monitor_email._send_err_email(module, title, subject, receiver_email)
			else:
				last_send_time = cls.__send_email_dict[module]
				if last_send_time < (_now + datetime.timedelta(minutes=-20)):
					cls.__send_email_dict[module] = _now
					monitor_email._send_err_email(module, title, receiver_email, subject)
				else:
					sd.log_info('The module of {0} has send err email in last 20 minutes'.format(module))
					return None
			
	@classmethod
	def send_email_direct(cls, module, title, subject, receiver_email):
		monitor_email = MonitEmialSender()
		if isinstance(receiver_email, str):
			email_list = receiver_email.split(',')
		elif isinstance(receiver_email, list):
			email_list = receiver_email
		else:
			email_list = []
		monitor_email._send_email(module, title, subject, email_list)

	@classmethod
	def send_message_direct(cls, module, title = '日志出现错误', phone_list=None):
		monitor_msg = MonitMsgSender()
		if isinstance(phone_list, str):
			phone_list = phone_list.split(',')
		elif isinstance(phone_list, list):
			phone_list = phone_list
		else:
			phone_list = []
		monitor_msg._send_message(module, title, phone_list)



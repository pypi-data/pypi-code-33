#!/usr/bin/env python
# -*- coding: utf-8 -*-
from .models import *
import datetime
import sense_core as sd
from . import email_base, utils
from .share_interface import Share

class MonitEmialSender(object):

	def send_email_with_db(self, module, title, subject):
		module_user = Share.get_module_config(module)
		email_list = Share.get_contact_list(module_user['user'], 'email')
		last_send_time = self._get_last_send_time(module)
		now = datetime.datetime.now()
		if last_send_time < (now + datetime.timedelta(minutes=-20)):
			send_res = self._send_err_email(module, title, subject, email_list)
			suc_email, fail_email = self._check_send_result(send_res)
			content = '(' + module + ') ' + title
			self._update_email_db(module, content, str(module_user['user']), suc_email, fail_email)
		else:
			sd.log_info('The module of {0} has send err message in last 20 minutes'.format(module))
			return None
	
	def _send_err_email(self, module, title,  subject, receiver_email):
		email_list = []
		if receiver_email:
			if type(receiver_email) == list:
				email_list = receiver_email
			elif type(receiver_email) == str:
				email_list = [receiver_email]
		else:
			return None
		send_res = self._send_email(module, title, subject, email_list)
		if not send_res or send_res == '':
			sd.log_info('[*] Module ' + module + ' errors email has send failed.')
		return send_res

	def _send_email(self, module, title, subject, email_list=None):
		_now = datetime.datetime.now()
		msg_res = self._send_email_detail(module, email_list, subject, title)
		return msg_res
	
	def _get_last_send_time(self, module_name):
		email_send_log = EmailSendLog()
		session = email_send_log.get_session()
		email_send = session.query(EmailSendLog).filter(EmailSendLog.module == module_name).order_by("time").all()
		if email_send:
			last_time = email_send[-1].time
		else:
			last_time = datetime.datetime.strptime("2019-01-01 00:00:00", "%Y-%m-%d %H:%M:%S")
		email_send_log.close_session(session)
		return last_time
	
	def _check_send_result(self, send_res):
		suc_email, fail_email = [], []
		if send_res['code'] == 'OK':
			suc_email = send_res['addr']
		elif send_res['code'] == 'Failed':
			suc_email = send_res['suc_list']
			fail_email = send_res['failed_list']
		return suc_email, fail_email
	
	def _update_email_db(self, module_name, content, uid, success_email, fail_email):
		email_send_log = EmailSendLog()
		session = email_send_log.get_session()
		_now = datetime.datetime.now()
		if success_email and len(success_email) != 0:
			for item in success_email:
				bulk_object = EmailSendLog(module=module_name, content=content, uids=uid, email=item,
										   status='success', time=_now)
				session.add(bulk_object)
		if fail_email and len(fail_email) != 0:
			for item in fail_email:
				bulk_object = EmailSendLog(module=module_name, content=content, uids=uid, email=item,
										   status='failed', time=_now)
				session.add(bulk_object)
		try:
			session.commit()
		except Exception as e:
			sd.log_warn('update err email db occur error:{0}'.format(e))
		finally:
			email_send_log.close_session(session)
	
	def _send_email_detail(self, module, email_list, subject, title):
		if not email_list or len(email_list) == 0:
			sd.log_info('The receiver email is empty')
			return {}
		_res = email_base.send_email(module, email_list, subject, title)
		res = self._is_mail_failed(_res)
		if res:
			_res = utils.build_dic(code='Failed', flag='email', failed_list=res)
		else:
			_res = utils.build_dic(code='OK', flag='email', addr=email_list)
			sd.log_info('email send successful!!!')
		return _res

	def _is_mail_failed(self, res):
		if not isinstance(res, dict):
			return []
		if len(res) == 0:
			return False
		return list(res.keys())


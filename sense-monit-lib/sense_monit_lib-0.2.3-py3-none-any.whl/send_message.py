#!/usr/bin/env python
# -*- coding: utf-8 -*-
from .models import *
import datetime
import sense_core as sd
from .share_interface import Share
from . import msg_base, utils
import time

class MonitMsgSender(object):

	def send_message_with_db(self, module, title):
		module_user = Share.get_module_config(module)
		phone_list = Share.get_contact_list(module_user['user'], 'phone')
		last_send_time = self._get_last_send_time(module)
		now = datetime.datetime.now()
		if last_send_time < (now + datetime.timedelta(minutes=-20)):
			send_res = self._send_err_message(module, title, phone_list)
			suc_phone, fail_phone = self._check_send_result(send_res)
			content = 'message:' + '(' + module + ') ' + title
			self._update_msg_db(module, content, str(module_user['user']), suc_phone, fail_phone)
		else:
			sd.log_info('The module of {0} has send err message in last 20 minutes'.format(module))
			return None
	
	def _send_err_message(self, module, title, phone_list):
		if phone_list:
			if type(phone_list) == list:
				phone_list = phone_list
			elif type(phone_list) == str:
				phone_list = [phone_list]
		else:
			return None
		send_res = self._send_message(module, title, phone_list)
		if not send_res:
			sd.log_info('[*] Module ' + module + ' errors message has been sent failed.')
		return send_res

	def _send_message(self, module, title, phone_list):
		msg_res = self._send_msg_detail(phone_list, module, title)
		return msg_res
	
	def _check_send_result(self, send_res):
		suc_phone, fail_phone = [], []
		if send_res['code'] == 'OK':
			suc_phone = send_res['addr']
		elif send_res['code'] == 'Failed':
			suc_phone = send_res['suc_list']
			fail_phone = send_res['failed_list']
		return suc_phone, fail_phone
	
	def _get_last_send_time(self, module_name):
		msg_send_log = MsgSendLog()
		session = msg_send_log.get_session()
		msg_send = session.query(MsgSendLog).filter(MsgSendLog.module == module_name).order_by("time").all()
		if msg_send:
			last_time = msg_send[-1].time
		else:
			last_time = datetime.datetime.strptime("2019-01-01 00:00:00", "%Y-%m-%d %H:%M:%S")
		msg_send_log.close_session(session)
		return last_time
	
	def _update_msg_db(self, module_name, content, uid, success_phone, fail_phone):
		msg_send_log = MsgSendLog()
		session = msg_send_log.get_session()
		_now = datetime.datetime.now()
		if success_phone and len(success_phone) != 0:
			for item in success_phone:
				bulk_object = MsgSendLog(module=module_name, content=content, uids=uid, phone=item,
										 status='success', time=_now)
				session.add(bulk_object)
		if fail_phone and len(fail_phone) != 0:
			for item in fail_phone:
				bulk_object = MsgSendLog(module=module_name, content=content, uids=uid, phone=item,
										 status='failed', time=_now)
				session.add(bulk_object)
		try:
			session.commit()
		except Exception as e:
			sd.log_warn('update err message db occur error:{0}'.format(e))
		finally:
			msg_send_log.close_session(session)
	
	def _send_msg_detail(self, phone_list, module, err_title):
		failed_list = []
		suc_list = []
		template_code = sd.config('aliyun_sms', 'msg_template', '')
		if template_code == '':
			sd.log_info('The template code is empty')
			return None
		if not phone_list or len(phone_list) == 0:
			sd.log_info('The receiver phone is empty')
			return None
		for phone in phone_list:
			if not phone:
				sd.log_info('[ALIYUN] ' + str(phone) + ' is not a phone number!')
				continue
			res = eval(
				msg_base.send_sms(phone, template_code, {'code': -9, 'message': '(' + module + ') ' + err_title}).decode())
			res_suc, res_failed = self._parse_msg_res(res, phone)
			suc_list.extend(res_suc)
			failed_list.extend(res_failed)
			time.sleep(2)
		if len(failed_list) == 0:
			res = utils.build_dic(code='OK', flag='message', addr=phone_list, content=template_code)
			sd.log_info('message send successful!!!')
		else:
			res = utils.build_dic(code='Failed', flag='message', content=template_code, failed_list=failed_list,
								  suc_list=suc_list)
		return res
	
	def _parse_msg_res(self, res, phone):
		failed_list = []
		suc_list = []
		if not isinstance(res, dict) or 'Code' not in res:
			return None
		if res['Code'] == 'OK':
			suc_list.append(phone)
		else:
			failed_list.append(phone)
		return suc_list, failed_list

#!/usr/bin/env python
# -*- coding: utf-8 -*-
from . import utils
from .models import *
import datetime


class Share(object):
	
	@classmethod
	def get_module_config(self, module):
		if not module or module == '':
			sd.log_info('The parameter of module is invaild')
			return None
		sd.log_info(module + ' is sending!')
		user_list = self.get_module_managers(module)
		if not user_list or len(user_list) == 0:
			sd.log_error(
				'[*] Module ' + module + ' is not configed in table "service_config".(or no duty person)')
		_res = utils.build_dic(module=module, user=user_list)
		return _res

	@classmethod
	def get_module_managers(self, module_name):
		service_config = ServiceConfig()
		session = service_config.get_session()
		res = session.query(ServiceConfig).filter(ServiceConfig.service_name == module_name).first()
		if not res:
			return None
		user_list = eval(res.uids)
		sd.log_info('The duty person of module:{} is {}'.format(module_name, user_list))
		service_config.close_session(session)
		return user_list
	
	@classmethod
	def error_log_detail(self, module_name):
		errorlog = ErrorLog()
		session = errorlog.get_session()
		_target_time = datetime.datetime.now() + datetime.timedelta(hours=-1)
		_time = datetime.datetime.strptime("2019-01-01 00:00:00", "%Y-%m-%d %H:%M:%S")
		err_object = session.query(ErrorLog).filter(ErrorLog.module_name == module_name).filter(ErrorLog.create_time >= _target_time).order_by('create_time').all()
		err_count = len(err_object) if err_object else 0
		last_err_content = err_object[-1].content if err_object else ''
		errorlog.close_session(session)
		return err_count, last_err_content
	
	@classmethod
	def get_contact_list(self, user_ids, field):
		supervisor = Supervisor()
		session = supervisor.get_session()
		sd_users = session.query(Supervisor).filter(Supervisor.id.in_(user_ids)).all()
		email_list = []
		phone_list = []
		for user in sd_users:
			if user.email and len(user.email) != 0:
				email_list.append(user.email)
			if user.phone and len(user.phone) != 0:
				phone_list.append(user.phone)
		supervisor.close_session(session)
		if field == 'email':
			sd.log_info('The email of duty person:{} is:{}'.format(user_ids, email_list))
			return email_list
		elif field == 'phone':
			sd.log_info('The phone of duty person:{} is:{}'.format(user_ids, phone_list))
			return phone_list
		return []

	@classmethod
	def list_config_module(cls):
		res = []
		service_config = ServiceConfig()
		session = service_config.get_session()
		config = list(session.query(ServiceConfig).all())
		for item in config:
			res.append(item.service_name)
		return res

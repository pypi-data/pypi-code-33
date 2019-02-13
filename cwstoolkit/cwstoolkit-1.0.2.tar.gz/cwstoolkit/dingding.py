#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author: Colinspace
# Date: 2018-12
# Desc:
# 


import json
import requests
import sys

if sys.version_info.major == 2:
    import ConfigParser as configparser
elif sys.version_info.major == 3:
    import configparser

# import configparser

class dingTalk():
	"""
	发送钉钉通知信息，包括 组机器人、企业通知
	"""

	_robot_url = "https://oapi.dingtalk.com/robot/send?access_token="

	def __init__(self, configfile='/etc/.dingtalk.conf', section='dingding', content=None, userlist=None, robottoken=None, msgtype="text", title=None, picurl=None, msgurl=None, mobiles=None, text=None):
		self.configfile = configfile,
		self.section = section
		self.content = content
		self.userlist = userlist
		self.robottoken = robottoken
		self.msgtype = msgtype
		self.title = title
		self.picurl = picurl
		self.msgurl = msgurl
		self.mobiles = mobiles
		self.text = text

	def getConfig(self):
		configdict = {}
		config = configparser.ConfigParser()
		config.read(self.configfile)
		configdict['corpid'] = config[self.section]['corpid']
		configdict['corpsecret'] = config[self.section]['corpsecret']
		configdict['agentid'] = config[self.section]['agentid']
		configdict['departmentid'] = config[self.section]['departmentid']

		return configdict

	def getToken(self):
		config = self.getConfig()
		corpid = config['corpid']
		corpsecret = config['corpsecret']
		url = 'https://oapi.dingtalk.com/gettoken?corpid=%s&corpsecret=%s' % (corpid, corpsecret)	
		response = requests.get(url)
		if response.status_code == 200:
			access_token = response.json()['access_token']
			return access_token

	def getDepartment(self):
		access_token = self.getToken()
		departmentid = self.getConfig['departmentid']
		url = "https://oapi.dingtalk.com/department/list_ids?access_token=%s&&id=%s" % (access_token,departmentid)
		response = requests.get(url)
		if response.status_code == 200:
			return response.json()['department']
	
	def getUser(self):
		"""或者给定部门下的所有用户"""
		access_token = self.getToken()
		departmentid = self.getConfig['departmentid']
		url = "https://oapi.dingtalk.com/user/simplelist?access_token=%s&department_id=%s" % (access_token,departmentid)
		response = requests.get(url)
		if response.status_code == 200:
			return response.json()['userlist']

	def sendRobot(self):
		dingurl = self._robot_url + self.robottoken

		data = """{
			"msgtype": "%s",
			"%s": {
				"title": "%s",
				"text": \"\"\"%s\"\"\",
				"picUrl": "%s",
				"messageUrl": "%s",
				"content":\"\"\"%s\"\"\"
			},
			"at": {
				"atMobiles": %s,
				"isAtAll": True
			}
		}""" % (self.msgtype, self.msgtype, self.title, self.text, self.picurl, self.msgurl, self.content, self.mobiles)
		## 调用request.post发送json格式的参数
		headers = {'Content-Type': 'application/json'}
		# result = requests.post(url=dingurl, data=json.dumps(data), headers=headers)
		result = requests.post(url=dingurl, data=json.dumps(eval(data)), headers=headers)

		## 判断是否发送成功
		if result.json()["errcode"] == 0:
			ret = {'code': 200, 'msg': 'send ding robot success !'}
		else:
			ret = {'code': '5001', 'msg': 'send ding robot failed !'}
		return ret 
	
	def sendWorkNote(self):
		config = self.getConfig()
		agentid = config['agentid']
		access_token = self.getToken()
		dingurl = "https://oapi.dingtalk.com/topapi/message/corpconversation/asyncsend_v2?access_token=%s" % access_token
		data = """{
			"agent_id": "%s",
			"userid_list": "%s",
			"msg": {
				"msgtype": "%s",
				"%s": {
					"title": "%s",
					"text": \"\"\"%s\"\"\",
					"picUrl": "%s",
					"messageUrl": "%s",
					"content":\"\"\"%s\"\"\"
				}
			}
		}""" % (agentid, self.userlist, self.msgtype, self.msgtype, self.title, self.content, self.picurl, self.msgurl, self.content)
		## 调用request.post发送json格式的参数
		headers = {'Content-Type': 'application/json'}
		result = requests.post(url=dingurl, data=json.dumps(eval(data)), headers=headers)
		## 判断是否发送成功
		if result.json()["errcode"] == 0:
			ret = {'code': 200, 'msg': 'send ding worknote success !'}
		else:
			ret = {'code': '5002', 'msg': 'send ding worknote failed !'}

		return ret


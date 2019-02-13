#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author: Colin
# Date: 2017-01-17
# Desc: 自定义一些工作中常用的时间函数
#

from datetime import datetime, date, timedelta
from cwstools.utilsLog import errorLog

__author__ = 'Colin'

def today(mode=1):
	"""
	return @str
	example: 2016-01-09
	if mode = 2 return 20160109
	"""
	if mode == 1:
		_today = date.today().strftime('%Y-%m-%d')
	elif mode == 2:
		_today = date.today().strftime('%Y%m%d')
	else:
		#colinLogs.errorLog("wrong mode here!,mode is 1 or 2")
		errorLog("wrong mode here!,mode is 1 or 2")

	return _today


def yesterday(mode=1):
	"""
	return @str
	example: 2016-01-09
	if mode = 2 return 20160109
	"""
	if mode == 1:
		yesterday = (datetime.today() - timedelta(days=1)).strftime('%Y-%m-%d')
	elif mode == 2:
		yesterday = (datetime.today() - timedelta(days=1)).strftime('%Y%m%d')
	else:
		errorLog("wrong mode here!,mode is 1 or 2")

	return yesterday

def tommorrow(mode=1):
	"""
	func: tommorrow
	return: the day after today
	if mode = 2 return 20160109
	"""
	if mode == 1:
		day = (datetime.today() + timedelta(days=1)).strftime('%Y-%m-%d')
	elif mode == 2:
		day = (datetime.today() + timedelta(days=1)).strftime('%Y%m%d')
	else:
		errorLog("wrong mode here!,mode is 1 or 2")

	return day

# def dayBefore(differ=1, mode=1):
# 	"""
# 	return @str
# 	if mode = 2 return 20160109
# 	"""
# 	if mode == 1:
# 		day = (datetime.today() - timedelta(days=differ)).strftime('%Y-%m-%d')
# 	elif mode == 2:
# 		day = (datetime.today() - timedelta(days=differ)).strftime('%Y%m%d')
# 	else:
# 		errorLog("wrong mode here!,mode is 1 or 2")

# 	return day

# def dayAfter(differ=1, mode=1):
# 	"""
# 	return @str
# 	if mode = 2 return 20160109
# 	"""
# 	if mode == 1:
# 		day = (datetime.today() + timedelta(days=differ)).strftime('%Y-%m-%d')
# 	elif mode == 2:
# 		day = (datetime.today() + timedelta(days=differ)).strftime('%Y%m%d')
# 	else:
# 		errorLog("wrong mode here!,mode is 1 or 2")

# 	return day


def diffDay(differ=1, mode=1):
	"""
	func: diffDay
	desc: 得到与当前day 相差 differ 个day的日期，mode 控制结果样式 
	return @str
	if mode = 2 return 20160109
	"""
	if mode == 1:
		day = (datetime.today() + timedelta(days=differ)).strftime('%Y-%m-%d')
	elif mode == 2:
		day = (datetime.today() + timedelta(days=differ)).strftime('%Y%m%d')
	else:
		errorLog("wrong mode here!,mode is 1 or 2")

	return day



def daytime(mode=1):
	"""
	func: daytime
	return @str
	if mode = 2 return 20160109
	"""
	if mode == 1:
		daytime =  datetime.today().strftime('%Y-%m-%d %H:%M:%S')
	elif mode == 2:
		daytime =  datetime.today().strftime('%Y%m%d %H:%M:%S')
	else:
		errorLog("wrong mode here!,mode is 1 or 2")

	return daytime

def firstAndLastDay(mode=1):
	"""
	func: firstAndLastDay
	desc: 得到上个月的第一天和最后一天
	return @str
	"""

	now = datetime.now()
	year = now.year
	month = now.month

	## 当月第一天
	cur_firstday = datetime(year, month, 1)
	print(type(cur_firstday))

	if month == 1:
		year -= 1
		month = 12
	else:
		month -= 1

	if mode == 1:
		## 上个月第一天
		last_firstday = datetime(year, month, 1).strftime('%Y-%m-%d')
		last_lastday = (cur_firstday - timedelta(days=1)).strftime('%Y-%m-%d')
	elif mode == 2:
		last_firstday = datetime(year, month, 1).strftime('%Y%m%d')
		last_lastday = (cur_firstday - timedelta(days=1)).strftime('%Y%m%d')
	else:
		errorLog("wrong mode here!,mode is 1 or 2")

	return last_firstday, last_lastday


def curHour(mode=1):
	"""
	func: curHour
	desc: 得到当前小时
	return @str
	"""
	if mode == 1:
		current_hour = datetime.now().strftime('%Y-%m-%d-%H')
	elif mode == 2:
		current_hour = datetime.now().strftime('%Y%m%d%H')
	else:
		errorLog("wrong mode here!,mode is 1 or 2")
	return current_hour

def diffHour(differ=1, mode=1):
	"""
	func: diffHour
	desc: 得到当前小时的前面或者后续 differ 个小时
	return @str
	"""
	if mode == 1:
		hour = (datetime.now() + timedelta(hours=differ)).strftime('%Y-%m-%d-%H')
	elif mode == 2:
		hour = (datetime.now() + timedelta(hours=differ)).strftime('%Y%m%d%H')
	else:
		errorLog("wrong mode here!,mode is 1 or 2")

	return hour


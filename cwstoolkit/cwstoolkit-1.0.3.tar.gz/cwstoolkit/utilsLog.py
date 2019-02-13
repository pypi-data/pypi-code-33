#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author: Colin
# Date: 2017-01-17
# Desc: 自定义带颜色的日志打印函数，按正常输出，错误，告警三个级别区别
#


from cwstools.utilsBase import colorMsg

def printLog(string):
	"""
	func: greenPrint
	return: log with green color for info log
	"""
	print(colorMsg('green', string))
	#print("\033[32m" + string + "\033[0m")

def warnLog(string):
	"""
	func: warnLog
	return: log with yellow color for warning message show
	"""
	#print("\033[33m" + string + "\033[0m")
	print(colorMsg('yellow', string))

def errorLog(string):
	"""
	func: warnLog
	return: log with yellow color for error message show
	"""
	#print("\033[31m" + string + "\033[0m")
	print(colorMsg('red', string))




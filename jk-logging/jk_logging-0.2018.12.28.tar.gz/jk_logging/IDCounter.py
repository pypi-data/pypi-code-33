#!/usr/bin/env python3
# -*- coding: utf-8 -*-



class IDCounter(object):

	def __init__(self):
		self.__value = 0

	def next(self):
		v = self.__value
		self.__value += 1
		return v

	@property
	def value(self):
		return self.__value

	def __int__(self):
		return self.__value

	def __str__(self):
		return str(self.__value)

	def __repr__(self):
		return str(self.__value)






#! /usr/bin/env python
# -*- coding: utf-8 -*-

from worksPersonas import WorksPersonas, DAU
from data import *

class Data(object):

	def __init__(self, aids):
		subjectDict, worksDict = createWorksDict(aids)
		self.dau = DAU()
		self.worksPersonas = WorksPersonas(worksDict.keys())

	def update(self):
		updateNewestActions(self.dau, self.worksPersonas)

	def save(self):
		self.dau.saveData()
		self.worksPersonas.saveData()

	#input 需要统计的主体列表,不传则统计全部
	#return 主体列表、作品列表
	def getSubWorksList(self, aids=[], blackVids=[]):
		return createWorksArgsList(self.worksPersonas, aids, blackVids)

	#return 当前的日活系数
	def getDauFactor(self):
		return self.dau.getDauFactor()

	#return 当天的新作品曝光数上限
	def getNewShowMax(self):
		return self.dau.getNewShowMax()

	#return 当前统计的最后时间
	def getFinalTime(self):
		return self.worksPersonas.lastPersonasTime





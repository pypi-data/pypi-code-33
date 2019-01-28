#! /usr/bin/env python
# -*- coding: utf-8 -*-
import time, gc
from .. import es

class DAU(object):

	def __init__(self):
		self.dayUids = {}
		data = es.searchStatisticsData('dau')
		while len(data) != 0:
			hit = data.pop()
			day = hit['_source']['day']
			uid = hit['_source']['uid']
			if not self.dayUids.has_key(day):
				self.dayUids[day] = []
			self.dayUids[day].append(uid)
		self.doc = []
		del data
		gc.collect()

	def saveData(self):
		if len(self.doc) != 0:
			es.updateStatisticsDoc('dau', self.doc)

	def getNewShowMax(self):
		dayTime = 24 * 60 * 60
		now = time.localtime(time.time())
		zeroTime = time.mktime((now.tm_year, now.tm_mon, now.tm_mday, 0, 0, 0, 0, 0, 0))
		rate = 0
		for index in range(1, 5):
			beforeCount = self.getDayCount(zeroTime - (index + 1) * dayTime)
			if beforeCount != 0:
				rate += (self.getDayCount(zeroTime - index * dayTime) - beforeCount) * 1.0 / beforeCount

		return max(self.getDayCount(zeroTime - dayTime) * (1 + rate / 5.0) * 0.01, 50)
	
	def getDauFactor(self):
		dayTime = 24 * 60 * 60
		now = time.localtime(time.time())
		zeroTime = time.mktime((now.tm_year, now.tm_mon, now.tm_mday, 0, 0, 0, 0, 0, 0))
		rate = 0
		for index in range(1, 5):
			beforeCount = self.getDayCount(zeroTime - (index + 1) * dayTime)
			if beforeCount != 0:
				rate += (self.getDayCount(zeroTime - index * dayTime) - beforeCount) * 1.0 / beforeCount

		activeDiv = self.getDayCount(zeroTime - dayTime) * (1 + rate / 5) * 0.4
		a = 1 / (5.5 * activeDiv) if activeDiv != 0 else 0
		return min(10, max(1, 1 / (a * len(self.dayUids[zeroTime])))) if self.dayUids.has_key(zeroTime) else 10

	def getDayCount(self, day):
		return len(self.dayUids[day]) if self.dayUids.has_key(day) else 0

	def addAction(self, uid, cTime):
		cLocalTime = time.localtime(cTime)
		day = time.mktime((cLocalTime.tm_year, cLocalTime.tm_mon, cLocalTime.tm_mday, 0, 0, 0, 0, 0, 0))
		if not self.dayUids.has_key(day):
			self.dayUids[day] = []
		if not uid in self.dayUids[day]:
			self.dayUids[day].append(uid)
			self.doc.append({"index":{"_id":str(day) + '$' + str(uid)}})
			self.doc.append({'day':day, 'uid':uid})

class WorksPersonas(object):

	DealFunc = {
		'1': 'Play',
		'2': 'Like',
		'3': 'CancelLike',
		'4': 'ShareF',
		'5': 'ShareI',
		'6': 'PlayTime',
		'7': 'Open',
		'9': 'Show',
		'10': 'Sub',
		'11': 'CancelSub'
	}

	def __init__(self, vids):
		with open('lastPersonasTime.ini', 'r') as f:
			self.lastPersonasTime = float(f.read())
		self.behaviors = {}
		start = 0
		while True: 
			body = {'size': 10000}
			if len(vids) != 0:
				end = min(len(vids), start + 1000)
				body['query'] = {'terms': {'vid': vids[start:end]}}
				start = end
			data = es.searchStatisticsDataByBody('works_personas', body)
			while len(data) != 0:
				hit = data.pop()
				info = hit['_source']
				if not info.has_key('recShow'):
					info['recShow'] = 0
				if not info.has_key('recShowPlay'):
					info['recShowPlay'] = 0
				self.behaviors[hit['_id']] = info
			del data
			gc.collect()
			if start == len(vids):
				break
		self.updateBehaviors = {}
		

	def saveData(self):
		if es.updateStatisticsData('works_personas', self.updateBehaviors):
			with open('lastPersonasTime.ini', 'w') as f:
				f.write(str(self.lastPersonasTime))

	def updateLastPersonasTime(self, newTime):
		newTime = es.esTimeToTime(newTime)
		if self.lastPersonasTime < newTime:
			self.lastPersonasTime = newTime

	def getBehavior(self, uid, vid):
		bid = str(uid) + '$' + vid
		if self.behaviors.has_key(bid):
			behavior = self.behaviors[bid]
		else:
			behavior = self.createBehavior(bid, uid, vid)
			self.behaviors[bid] = behavior
		self.updateBehaviors[bid] = behavior
		return behavior

	def createBehavior(self, bid, uid, vid):
		return {'bid': bid, 'uid': uid, 'vid': vid, 'play': 0, 'like': False, 'shareF': 0, 'shareI': 0, 'maxPlayTime': 0, 'playTime': 0, 'timeCount': 0, 'show': 0, 'showPlay': 0, 'recShow': 0, 'recShowPlay': 0, 'subAdd': 0}

	def addAction(self, uid, cTime, page, actionId, args):
		if WorksPersonas.DealFunc.has_key(actionId):
			eval('WorksPersonas.action' + WorksPersonas.DealFunc[actionId])(self, uid, page, args)

	def actionPlay(self, uid, page, args):
		self.getBehavior(uid, args[0])['play'] += 1

	def actionLike(self, uid, page, args):
		self.getBehavior(uid, args[0])['like'] = True

	def actionCancelLike(self, uid, page, args):
		self.getBehavior(uid, args[0])['like'] = False

	def actionShareF(self, uid, page, args):
		self.getBehavior(uid, args[0])['shareF'] += 1

	def actionShareI(self, uid, page, args):
		self.getBehavior(uid, args[0])['shareI'] += 1

	def actionPlayTime(self, uid, page, args):
		behavior = self.getBehavior(uid, args[0])
		playTime = int(args[1])
		behavior['maxPlayTime'] = max(behavior['maxPlayTime'], playTime)
		behavior['playTime'] += playTime
		behavior['timeCount'] += 1

	def actionOpen(self, uid, page, args):
		if page == 'pages/common/videoplay/videoplay' and len(args) > 2 and args[0] == '1' and args[2] in ['1', '2', '3', '4']:
			behavior = self.getBehavior(uid, args[1])
			behavior['showPlay'] += 1
			if args[2] == '4':
				behavior['recShowPlay'] += 1

	def actionShow(self, uid, page, args):
		if args[1] in ['0', '1', '20', '3']:
			behavior = self.getBehavior(uid, args[0])
			behavior['show'] += 1
			if args[1] == '3':
				behavior['recShow'] += 1

	def actionSub(self, uid, page, args):
		if len(args) > 1:
			self.getBehavior(uid, args[1])['subAdd'] += 1

	def actionCancelSub(self, uid, page, args):
		if len(args) > 1:
			self.getBehavior(uid, args[1])['subAdd'] -= 1




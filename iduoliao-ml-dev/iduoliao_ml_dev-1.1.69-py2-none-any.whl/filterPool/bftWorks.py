#! /usr/bin/env python
# -*- coding: utf-8 -*-

import time, json
from .. import es

class BftWorks(object):

	RiseThreshold = 0.3

	PoolLevelMax = 3

	ShowMax = {0: 50, 1: 100, 2: 500}

	Weights = {0: {"like": 1.5, "share": 1.5, "longPlay": 1, "play": 1}
	, 1: {"like": 2, "share": 2, "longPlay": 1, "play": 1}
	, 2: {"like": 2, "share": 3, "longPlay": 1, "play": 1}}

	#1 正常 2 晋级 3 待定 4 淘汰
	Status = {'Normal': 1, 'Success': 2, 'Await': 3, 'Fail': 4}

	def __init__(self, vid):
		self.vid = vid
		self.records = []
		self.score = 0
		self.enterPool(0)

	def updateAction(self, action):
		if self.status in [BftWorks.Status['Success'], BftWorks.Status['Fail']]:
			return

		actionId = action['action']
		uid = action['uid']
		if actionId == 3:
			self.uidSetDict['show'].add(uid)
		elif actionId == 16:
			self.uidSetDict['like'].add(uid)
		elif actionId == 12 or actionId == 13:
			self.uidSetDict['share'].add(uid)
		elif actionId == 2:
			self.uidSetDict['longPlay'].add(uid)
		elif actionId == 5:
			self.uidSetDict['play'].add(uid)

	def updateStatus(self):
		if self.status in [BftWorks.Status['Success'], BftWorks.Status['Fail']]:
			return

		pool = self.getPool()
		showMax = BftWorks.ShowMax[pool]
		weight = BftWorks.Weights[pool]

		show = self.getCount('show')
		score = 0
		totalOne = 0
		for key in weight.keys():
			score += weight[key] * self.getCount(key)
			totalOne += weight[key]
		
		if score >= max(showMax, show) * totalOne * BftWorks.RiseThreshold:
			self.rise()
		elif show >= showMax:
			self.status = BftWorks.Status['Await']

		self.score = score

	def updateHistoryActions(self, endTime):
		if self.status in [BftWorks.Status['Success'], BftWorks.Status['Fail']]:
			return

		body = {"query": {"bool": {"must": [{"range": {"time": {"gte": self.records[0]['time'] * 1000, "lt": endTime * 1000}}}, {"term": {"vid": self.vid}}, {"terms": {"action": [2, 3, 5, 12, 13, 16]}}]}}, "size": 0, "aggs": {}}
		body['aggs']['uid_diff'] = {"terms": {"field": "action", "size": 6}, "aggs": {"count": {"cardinality": {"field": "uid"}}}}
		aggs = es.searchStatisticsAggs('works_actions', body)
		
		counts = {2: 0, 3: 0, 5: 0, 12: 0, 13: 0, 16: 0}
		for bucket in aggs['uid_diff']['buckets']:
			counts[bucket['key']] = bucket['count']['value']

		self.historyData['show'] = counts[3]
		self.historyData['like'] = counts[16]
		self.historyData['share'] = counts[12] + counts[13]
		self.historyData['longPlay'] = counts[2]
		self.historyData['play'] = counts[5]

		self.updateStatus()

	def isResurgence(self):
		return self.records[0]['riseType'] == 3

	def resurgence(self):
		self.enterPool(self.getPool(), 3)

	#1 正常晋级（默认） 2 候补补齐
	def rise(self, riseType=1):
		pool = self.getPool()
		if pool >= BftWorks.PoolLevelMax - 1:
			self.status = BftWorks.Status['Success']
		else:
			self.enterPool(pool + 1, riseType)

	def fail(self):
		self.status = BftWorks.Status['Fail']

	#1 正常晋级（默认） 2 候补补齐  3 复活进入
	def enterPool(self, newPool, riseType=1):
		self.records[0]['score'] = self.score
		self.records.insert(0, {'pool': newPool, 'time': int(time.time()), 'riseType': riseType, 'score': 0})

		self.score = 0
		self.status = BftWorks.Status['Normal']
		self.historyData = {'show': 0, 'like': 0, 'share': 0, 'longPlay': 0, 'play': 0}
		self.uidSetDict = {'show': set(), 'like': set(), 'share': set(), 'longPlay': set(), 'play': set()}

	def getPool(self):
		return self.records[0]['pool']

	def getCount(self, key):
		return self.historyData[key] + len(self.uidSetDict[key])

	def toSaveEsData(self):
		data = {"vid": self.vid, 'score': self.score, 'show': self.getCount('show')}
		for key in BftWorks.Weights[self.pool].keys():
			data[key] = self.getCount(key)
		return data

	def syncEsData(self, source):
		self.pool = source["pool"]
		self.timeEnter = source["timeEnter"]
	


	
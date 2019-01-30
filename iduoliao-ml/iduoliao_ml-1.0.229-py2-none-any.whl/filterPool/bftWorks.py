#! /usr/bin/env python
# -*- coding: utf-8 -*-

from .. import es

#pool: 1 一层流量池 2 二层流量池 3 三层流量池 4 晋级池 5 淘汰池
class BftWorks(object):

	ShowMax = {1: 50, 2: 100, 3: 500}

	Weights = {1: {"like": 1.5, "share": 1.5, "longPlay": 1, "play": 1}
	, 2: {"like": 2, "share": 2, "longPlay": 1, "play": 1}
	, 3: {"like": 2, "share": 3, "longPlay": 1, "play": 1}}

	def __init__(self, vid):
		self.vid = vid
		self.pool = 1
		self.timeEnter = es.timeToEsLocalTime(time.time())
		self.show = 0
		self.score = 0

		self.showUids = set()
		self.likeUids = set()
		self.shareUids = set()
		self.longPlayUids = set()
		self.playUids = set()

	def updateAction(self, action):
		actionId = action['action']
		uid = action['uid']
		if actionId == 3:
			self.showUids.add(uid)
		elif actionId == 16:
			self.likeUids.add(uid)
		elif actionId == 12 or actionId == 13:
			self.shareUids.add(uid)
		elif actionId == 5:
			self.playUids.add(uid)

		self.updateStatus()

	def updateStatus(self):
		pass


	def update(self):
		body = {"query": {"bool": {"must": [{"range": {"time": {"gte": self.timeEnter}}}, {"term": {"vid": self.vid}}, {"terms": {"action": [2, 3, 5, 12, 13, 16]}}]}}, "size": 0, "aggs": {}}
		body['aggs']['uid_diff'] = {"terms": {"field": "action", "size": 6}, "aggs": {"count": {"cardinality": {"field": "uid"}}}}
		aggs = es.searchStatisticsAggs('works_actions', body)
		
		counts = {2: 0, 3: 0, 5: 0, 12: 0, 13: 0, 16: 0}
		for bucket in aggs['uid_diff']['buckets']:
			counts[bucket['key']] = bucket['count']['value']

		weight = BftWorks.Weights[self.pool]
		showMax = BftWorks.ShowMax[self.pool]

		self.show = counts[3]
		self.score = weight['like'] * counts[16] + weight['share'] * (counts[12] + counts[13]) + weight['longPlay'] * counts[2] + weight['play'] * counts[5]
		
		if self.score >= max(showMax, self.show) * (weight['like'] + weight['share'] + weight['longPlay'] + weight['play']) * 0.3
			self.pool += 1
			self.timeEnter = es.timeToEsLocalTime(time.time())
		elif self.show >= showMax:
			self.pool = 5
			self.timeEnter = es.timeToEsLocalTime(time.time())

	def toSaveEsData(self):
		return {"vid": self.vid, "pool": self.pool, "timeEnter": self.timeEnter}

	def syncEsData(self, source):
		self.pool = source["pool"]
		self.timeEnter = source["timeEnter"]
	


	
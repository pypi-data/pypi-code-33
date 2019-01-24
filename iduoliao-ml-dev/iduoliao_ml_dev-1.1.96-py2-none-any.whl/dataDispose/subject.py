#! /usr/bin/env python
# -*- coding: utf-8 -*-

import gc, time, threading
from .. import es

class Subject(object):

	def __init__(self, aid):
		self.aid = aid
		self.startTime = -1
		self.endTime = 0
		self.count = 0
		self.play = 0
		self.replay = 0
		self.conv = 0

	def toSaveEsData(self):
		return {"aid": self.aid, "score": self.score, "time": self.endTime}

	def updateActions(self, endTime, startTime=0):
		self.startTime = min(self.startTime, startTime) if self.startTime != -1 else startTime
		self.endTime = max(self.endTime, endTime)
		count, play, replay, conv = self.getDataByAid(self.aid, startTime, endTime)
		self.count += count
		self.play += play
		self.replay += replay
		self.conv = (self.conv + conv) / 2.0 if self.conv != 0 else conv
		gc.collect()

	def getDataByAid(self, aid, startTime, endTime):

		recShow = 0
		recShowPlay = 0

		body = {"query": {"bool": {"must": [{"range": {"createTime": {"gte": startTime, "lt": endTime}}}, {"term": {"aid": aid}}, {"terms": {"action": [3, 5]}}]}}, "size": 0, "aggs": {}}
		body['aggs']['uid_diff'] = {"terms": {"field": "action", "size": 2}, "aggs": {"count": {"cardinality": {"field": "uid"}}}}
		aggs = es.searchStatisticsAggs('works_actions', body)

		counts = {3: 0, 5: 0}
		for bucket in aggs['uid_diff']['buckets']:
			counts[bucket['key']] = bucket['count']['value'] 

		return 0, 0, 0, counts[5] * 1.0 / counts[3] if counts[3] != 0 else 0

	'''
	def getDataByAid(self, aid, startTime, endTime):
		hits = es.searchStatisticsDataByBody("works_actions", {"query": {"bool": {"must": [{"range": {"createTime": {"gte": startTime, "lt": endTime}}}, {"term": {"aid": aid}}, {"terms": {"action": [3, 5]}}]}}}, True, False)
		count = 0
		playUids = []
		replayUids = set()
		recShow = 0
		recShowPlay = 0
		for hit in hits:
			action = hit['_source']
			actionId = action['action']
			uid = action['uid']
			if actionId == 1:
				if uid in playUids:
					replayUids.add(uid)
				else:
					playUids.append(uid)
			elif actionId == 3:
				recShow += 1
			elif actionId == 4:
				count += 1
			elif actionId == 5:
				recShowPlay += 5
		return count, len(playUids), len(replayUids), recShowPlay * 1.0 / recShow if recShow != 0 else 0
	'''

class SubjectThread(threading.Thread):

	def __init__(self, subject, endTime):
		threading.Thread.__init__(self)
		self.subject = subject
		self.endTime = endTime

	def run(self):
		self.subject.updateActions(self.endTime)


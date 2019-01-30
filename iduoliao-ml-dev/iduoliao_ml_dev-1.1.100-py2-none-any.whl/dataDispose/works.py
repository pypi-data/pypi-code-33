#! /usr/bin/env python
# -*- coding: utf-8 -*-

import gc, time, threading
from .. import es

class Works(object):

	DurationSections = [0, 30, 60, 180, 300, 600, 900, 1200, 1800, 2400, 3600, 7200]

	def __init__(self, vid, aid, title, publishTime, duration):
		self.vid = vid
		self.aid = aid
		self.title = title
		self.publishTime = int(time.time() - es.esTimeToTime(publishTime, True)) / 3600
		durationIndex = 7200
		for value in Works.DurationSections:
			if duration < value:
				durationIndex = value
				break
		self.durationIndex = durationIndex
		self.startTime = -1
		self.endTime = 0
		self.play = 0
		self.shareF = 0
		self.shareI = 0
		self.replay = 0
		self.like = 0
		self.sub = 0
		self.longPlay = 0
		self.timeAvg = 0
		self.score = 0
		self.ratio = 0
		self.resShow = 0
		self.resShowPlay = 0

		self.playUids = []
		self.shareFUids = set()
		self.shareIUids = set()
		self.replayUids = set()
		self.timeTotal = 0
		self.timeCount = 0

	def updateAction(self, action):
		actionId = action['action']
		uid = action['uid']
		if actionId == 1:
			self.timeTotal += action['value']
			self.timeCount += 1
			self.timeAvg = self.timeTotal * 1.0 / self.timeCount
			if uid in self.playUids:
				self.replayUids.add(uid)
				self.replay = len(self.replayUids)
			else:
				self.playUids.append(uid)
				self.play = len(self.playUids)
		elif actionId == 12:
			self.shareFUids.add(uid)
			self.shareF = len(self.shareFUids)
		elif actionId == 13:
			self.shareIUids.add(uid)
			self.shareI = len(self.shareIUids)
		elif actionId == 14:
			self.like += 1
		elif actionId == 15:
			self.like -= 1
		elif actionId == 16:
			self.sub += 1
		elif actionId == 17:
			self.sub -= 1
		elif actionId == 2:
			self.longPlay += 1

	def toSaveEsData(self):
		return {"vid": self.vid, "score": self.score, "time": self.endTime, "ratio": self.ratio, "aid": self.aid, "title": self.title, "play": self.play, "shareF": self.shareF, "shareI": self.shareI, "replay": self.replay, "sub": self.sub, "like": self.like, "longPlay": self.longPlay, "timeAvg": self.timeAvg, "resShow": self.resShow, "resShowPlay": self.resShowPlay}

	def updateActions(self, endTime, startTime=0):
		self.startTime = min(self.startTime, startTime) if self.startTime != -1 else startTime
		self.endTime = max(self.endTime, endTime)
		play, shareF, shareI, replay, like, sub, longPlay, timeAvg, resShow, resShowPlay = self.getDataByVid(self.vid, startTime, endTime)
		self.play += play
		self.shareF += shareF
		self.shareI += shareI
		self.replay += replay
		self.like += like
		self.sub += sub
		self.longPlay += longPlay
		self.timeAvg = (self.timeAvg + timeAvg) / 2.0 if self.timeAvg != 0 else timeAvg
		self.resShow += resShow
		self.resShowPlay += resShowPlay
		gc.collect()

	def getDataByVid(self, vid, startTime, endTime):
		#now = time.time()

		body = {"query": {"bool": {"must": [{"range": {"createTime": {"gte": startTime, "lt": endTime}}}, {"term": {"vid": vid}}, {"terms": {"action": [2, 3, 5, 12, 13, 14, 15, 16, 17]}}]}}, "size": 0, "aggs": {}}
		body['aggs']['uid_diff'] = {"terms": {"field": "action", "size": 7}, "aggs": {"count": {"cardinality": {"field": "uid"}}}}
		aggs = es.searchStatisticsAggs('works_actions', body)

		#print(time.time() - now)
		
		counts = {2: 0, 3: 0, 5:0, 12: 0, 13: 0, 14: 0, 15: 0, 16: 0, 17: 0}
		for bucket in aggs['uid_diff']['buckets']:
			counts[bucket['key']] = bucket['count']['value']

		body = {"query": {"bool": {"must": [{"range": {"createTime": {"gte": startTime, "lt": endTime}}}, {"term": {"vid": vid}}, {"term": {"action": {"value": 1}}}]}}, "size": 0, "aggs": {}}
		body['aggs']['time_avg'] = {"avg": {"field": "value"}}
		timeAvg = es.searchStatisticsAggs('works_actions', body)['time_avg']['value']

		#print(time.time() - now)

		replay = 0
		hits = es.searchStatisticsDataByBody("works_players", {"query": {"term": {"vid": vid}}, "size": 10000}, True, False, True)
		for hit in hits:
			if hit['_version'] >= 2:
				replay += 1

		#print(time.time() - now)

		#print(len(hits), counts[12], counts[13], replay, counts[16] - counts[17], counts[14] - counts[15], counts[2], timeAvg if timeAvg != None else 0)
		return len(hits), counts[12], counts[13], replay, counts[16] - counts[17], counts[14] - counts[15], counts[2], timeAvg if timeAvg != None else 0, counts[3], counts[5]


	'''
	def getDataByVid(self, vid, startTime, endTime):
		hits = es.searchStatisticsDataByBody("works_actions", {"query": {"bool": {"must": [{"range": {"createTime": {"gte": startTime, "lt": endTime}}}, {"term": {"vid": vid}}, {"terms": {"action": [1, 2, 12, 13, 14, 15, 16, 17]}}]}}}, True, False)
		playUids = []
		shareFUids = set()
		shareIUids = set()
		replayUids = set()
		like = 0
		sub = 0
		longPlay = 0
		timeTotal = 0
		timeCount = 0
		for hit in hits:
			action = hit['_source']
			actionId = action['action']
			uid = action['uid']
			if actionId == 1:
				timeTotal += action['value']
				timeCount += 1
				if uid in playUids:
					replayUids.add(uid)
				else:
					playUids.append(uid)
			elif actionId == 12:
				shareFUids.add(uid)
			elif actionId == 13:
				shareIUids.add(uid)
			elif actionId == 14:
				like += 1
			elif actionId == 15:
				like -= 1
			elif actionId == 16:
				sub += 1
			elif actionId == 17:
				sub -= 1
			elif actionId == 2:
				longPlay += 1
		return len(playUids), len(shareFUids), len(shareIUids), len(replayUids), like, sub, longPlay, timeTotal * 1.0 / timeCount if timeCount != 0 else 0
	'''


class WorksThread(threading.Thread):

	def __init__(self, works, endTime):
		threading.Thread.__init__(self)
		self.works = works
		self.endTime = endTime

	def run(self):
		self.works.updateActions(self.endTime)



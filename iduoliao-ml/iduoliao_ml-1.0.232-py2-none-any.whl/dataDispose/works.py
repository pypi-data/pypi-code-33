#! /usr/bin/env python
# -*- coding: utf-8 -*-

import gc, time, threading
from .. import es

class Works(object):

	def __init__(self, vid, aid, title, publishTime, videourl, duration):
		self.vid = vid
		self.aid = aid
		self.title = title
		self.publishTime = int(time.time() - es.esTimeToTime(publishTime, True)) / 3600
		self.videourl = videourl
		self.duration = duration
		self.startTime = -1
		self.endTime = -1

		self.play = 0
		self.share = 0
		self.like = 0
		self.sub = 0
		#self.longPlay = 0
		self.resShow = 0
		self.resShowPlay = 0
		self.timeCount = 0
		self.timeTotal = 0

		self.score = 0

		self.playUids = set()
		self.shareUids = set()
		#self.longPlayUids = set()
		self.resShowUids = set()
		self.resShowPlayUids = set()

		self.historyPlay = 0
		self.historyShare = 0
		#self.historyLongPlay = 0
		self.historyResShow = 0
		self.historyResShowPlay = 0

	def updateHistory(self, history):
		self.historyPlay = history['play']
		self.play = len(self.playUids) + self.historyPlay
		self.historyShare = history['share']
		self.share = len(self.shareUids) + self.historyShare
		self.like += history['like']
		self.sub += history['sub']
		#self.historyLongPlay = history['longPlay']
		#self.longPlay = len(self.longPlayUids) + self.historyLongPlay
		self.historyResShow = history['resShow']
		self.resShow = len(self.resShowUids) + self.historyResShow
		self.historyResShowPlay = history['resShowPlay']
		self.resShowPlay = len(self.resShowPlayUids) + self.historyResShowPlay
		self.timeCount += history['timeCount']
		self.timeTotal += history['timeTotal']

	'''
	def updateAction(self, action):
		actionId = action['action']
		uid = action['uid']
		if actionId == 1:
			self.playUids.add(uid)
			self.play = len(self.playUids) + self.historyPlay
			self.timeCount += 1
			self.timeTotal += action['value']
		elif actionId == 12 and actionId == 13:
			self.shareUids.add(uid)
			self.share = len(self.shareUids) + self.historyShare
		elif actionId == 14:
			self.like += 1
		elif actionId == 15:
			self.like -= 1
		elif actionId == 16:
			self.sub += 1
		elif actionId == 17:
			self.sub -= 1
		elif actionId == 3:
			self.resShowUids.add(uid)
			self.resShow = len(self.resShowUids) + self.historyResShow
		elif actionId == 5:
			self.resShowPlayUids.add(uid)
			self.resShowPlay = len(self.resShowPlayUids) + self.historyResShowPlay
	'''
	def updateAction(self, action):
		actionId = action['action']
		uid = action['uid']
		if actionId == 8:
			self.playUids.add(uid)
			self.play = len(self.playUids) + self.historyPlay
			self.timeCount += 1
			self.timeTotal += action['value']
		elif actionId == 9:
			self.shareUids.add(uid)
			self.share = len(self.shareUids) + self.historyShare
		elif actionId == 4:
			self.like += 1
		elif actionId == 5:
			self.like -= 1
		elif actionId == 6:
			self.sub += 1
		elif actionId == 7:
			self.sub -= 1
		elif actionId == 1:
			self.resShowUids.add(uid)
			self.resShow = len(self.resShowUids) + self.historyResShow
		elif actionId == 2:
			self.resShowPlayUids.add(uid)
			self.resShowPlay = len(self.resShowPlayUids) + self.historyResShowPlay

	def toSaveEsData(self):
		return {"vid": self.vid, "score": self.score, "time": self.endTime, "aid": self.aid, "title": self.title, "play": self.play, "share": self.share, "sub": self.sub, "like": self.like, "resShow": self.resShow, "resShowPlay": self.resShowPlay, "videourl": self.videourl, "timeCount": self.timeCount, "timeTotal": self.timeTotal, "duration": self.duration}

	def updateActions(self, endTime, startTime=0, needCreateLimit=False):
		self.startTime = min(self.startTime, startTime) if self.startTime != -1 else startTime
		self.endTime = max(self.endTime, endTime)
		play, share, like, sub, resShow, resShowPlay, timeCount, timeTotal = self.getHotDataByVid(self.vid, startTime, endTime, needCreateLimit)
		self.play = play
		self.share = share
		self.like = like
		self.sub = sub
		self.resShow = resShow
		self.resShowPlay = resShowPlay
		self.timeCount = timeCount
		self.timeTotal = timeTotal
		gc.collect()

	def getHotDataByVid(self, vid, startTime, endTime, needCreateLimit):

		baseBody = {"query": {"bool": {"must": [{"range": {"time": {"gte": int(startTime * 1000), "lt": int(endTime * 1000)}}}, {"term": {"vid": vid}}]}}, "size": 0, "aggs": {}}
		if needCreateLimit:
			baseBody['query']['bool']['must'].append({"range": {"createTime": {"lt": endTime}}})

		body = baseBody
		#body['query']['bool']['must'].append({"terms": {"action": [1, 2, 3, 4, 5, 6, 7, 8, 9]}})
		body['aggs']['uid_diff'] = {"terms": {"field": "action", "size": 9}, "aggs": {"count": {"cardinality": {"field": "uid"}}}}
		aggs = es.searchStatisticsAggs('hot_actions', body)
		
		timeCount = 0
		counts = {1: 0, 2: 0, 3: 0, 4: 0, 5: 0, 6: 0, 7: 0, 8: 0, 9: 0}
		for bucket in aggs['uid_diff']['buckets']:
			counts[bucket['key']] = bucket['count']['value']
			if bucket['key'] == 8:
				timeCount = bucket['doc_count']

		body = baseBody
		body['query']['bool']['must'].append({"term": {"action": {"value": 8}}})
		body['aggs']['time_total'] = {"sum": {"field": "value"}}
		timeTotal = es.searchStatisticsAggs('hot_actions', body)['time_total']['value']

		return counts[8], counts[9], counts[4] - counts[5], counts[6] - counts[7], counts[1], counts[2], timeCount, timeTotal

	def getDataByVid(self, vid, startTime, endTime, needCreateLimit):
		#now = time.time()

		baseBody = {"query": {"bool": {"must": [{"range": {"time": {"gte": int(startTime * 1000), "lt": int(endTime * 1000)}}}, {"term": {"vid": vid}}]}}, "size": 0, "aggs": {}}
		if needCreateLimit:
			baseBody['query']['bool']['must'].append({"range": {"createTime": {"lt": endTime}}})

		body = baseBody
		body['query']['bool']['must'].append({"terms": {"action": [1, 3, 5, 12, 13, 14, 15, 16, 17]}})
		body['aggs']['uid_diff'] = {"terms": {"field": "action", "size": 9}, "aggs": {"count": {"cardinality": {"field": "uid"}}}}
		aggs = es.searchStatisticsAggs('works_actions', body)

		#print(time.time() - now)
		
		timeCount = 0
		counts = {1: 0, 3: 0, 5: 0, 12: 0, 13: 0, 14: 0, 15: 0, 16: 0, 17: 0}
		for bucket in aggs['uid_diff']['buckets']:
			counts[bucket['key']] = bucket['count']['value']
			if bucket['key'] == 1:
				timeCount = bucket['doc_count']

		body = baseBody
		body['query']['bool']['must'].append({"term": {"action": {"value": 1}}})
		body['aggs']['time_total'] = {"sum": {"field": "value"}}
		timeTotal = es.searchStatisticsAggs('works_actions', body)['time_total']['value']

		'''
		body = {"query": {"bool": {"must": [{"range": {"createTime": {"gte": startTime, "lt": endTime}}}, {"term": {"vid": vid}}, {"term": {"action": {"value": 1}}}]}}, "size": 0, "aggs": {}}
		body['aggs']['time_avg'] = {"avg": {"field": "value"}}
		timeAvg = es.searchStatisticsAggs('works_actions', body)['time_avg']['value']

		#print(time.time() - now)
		
		replay = 0
		hits = es.searchStatisticsDataByBody("works_players", {"query": {"term": {"vid": vid}}, "size": 10000}, True, False, True)
		for hit in hits:
			if hit['_version'] >= 2:
				replay += 1
		'''
		#print(time.time() - now)

		#print(len(hits), counts[12], counts[13], replay, counts[16] - counts[17], counts[14] - counts[15], counts[2], timeAvg if timeAvg != None else 0)
		return counts[1], counts[12] + counts[13], counts[16] - counts[17], counts[14] - counts[15], counts[3], counts[5], timeCount, timeTotal


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

	def __init__(self, works, endTime, startTime=0, needCreateLimit=False):
		threading.Thread.__init__(self)
		self.works = works
		self.endTime = endTime
		self.startTime = startTime
		self.needCreateLimit = needCreateLimit

	def run(self):
		self.works.updateActions(self.endTime, self.startTime, self.needCreateLimit)



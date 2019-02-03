#! /usr/bin/env python
# -*- coding: utf-8 -*-

import sys, time, gc, threading, MySQLdb
from .. import es, imatrix
from works import Works, WorksThread
from subject import Subject, SubjectThread

MaxThreadCount = 3

#删除2个月半之前作品的推荐记录
def deletePastWorksRecord():
	vids = []
	for hit in es.scrollSearch('works_video_read', 'video', {"query": {"range": {"publishtime": {"lt": getDayBeforeTime(75)}}}, "size":1000}):
		vids.append(hit['_id'])
		if len(vids) == 1000:
			if not deletePastWorksRecordOnce(vids):
				return False
			vids = []
	return deletePastWorksRecordOnce(vids)

def deletePastWorksRecordOnce(vids):
	return es.deleteStatisticsData('statistics_works_hot_fixed', {"query": {"terms": {"_routing": vids}}}, "recommendviewrecordsearch") and es.deleteStatisticsData('statistics_works_hot_fixed_backups', {"query": {"terms": {"_routing": vids}}}, "recommendviewrecordsearch")

def getDauFactor():
	zeroTime = getZeroTime() * 1000
	startTime = long(zeroTime - 6 * 24 * 60 * 60 * 1000)
	endTime = long(time.time() * 1000)

	body = {"query": {"range": {"time": {"gte": startTime, "lte": endTime}}}, "size": 0, "aggs": {"dau": {"date_histogram": {"field": "time", "interval": "day", "time_zone":"+08:00", "min_doc_count": 0, "extended_bounds": {"min": startTime, "max": endTime}, "order": {"_key": "asc"}}, "aggs": {"count": {"cardinality": {"field": "uid"}}}}}}
	buckets = es.searchStatisticsAggs('works_actions', body)['dau']['buckets']

	#print(buckets)
	rate = 0
	for index in range(1, 5):
		beforeCount = buckets[index - 1]['count']['value']
		if beforeCount != 0:
			rate += (buckets[index]['count']['value'] - beforeCount) * 1.0 / beforeCount

	activeDiv = buckets[5]['count']['value'] * (1 + rate / 5) * 0.4
	a = 1 / (5.5 * activeDiv) if activeDiv != 0 else 0
	todayDau = buckets[6]['count']['value']
	return min(10, max(1, 1 / (a * todayDau))) if todayDau != 0 else 1

def getSubjectHistory():
	subjectHistory = {}
	for hit in es.searchStatisticsData('subject_history'):
		history = hit['_source']
		subjectHistory[history['aid']] = history
	return subjectHistory

def getWorksHistory():
	worksHistory = {}
	for hit in es.searchStatisticsData('works_history'):
		history = hit['_source']
		worksHistory[history['vid']] = history
	return worksHistory

def getWorksList():
	worksList = []
	
	#取最近2个月的authorstate和state都是正常的作品
	for hit in es.scrollSearch('works_video_read', 'video', {"query": {"bool": {"must": [{"term": {"state": {"value": 0}}}, {"term": {"authorstate": {"value": 0}}}, {"range": {"publishtime": {"gte": getDayBeforeTime(60)}}}]}}, "size":1000}):
		works = toWorks(hit['_source'])
		if works != None:
			worksList.append(works)
	return worksList

def updateHistoryActions():
	worksList = getWorksList()
	subjectList = []

	endTime = getZeroTime()

	worksThreads = []

	while len(worksList) != 0:
		if len(threading.enumerate()) > MaxThreadCount:
			#time.sleep(1)
			pass
		else:
			works = worksList.pop()
			print(len(worksList), works.vid, works.aid)
			t = WorksThread(works, endTime)
			worksThreads.append(t)
			t.setDaemon(True)
			t.start()

	while len(threading.enumerate()) != 1:
		#time.sleep(1)
		pass

	subjectAids = []

	for t in worksThreads:
		works = t.works
		worksList.append(works)
		aid = works.aid

		if aid not in subjectAids:
			subjectAids.append(aid)
			subject = Subject(aid)
			subjectList.append(subject)
		else:
			subject = subjectList[subjectAids.index(aid)]
		subject.count += 1
		subject.play += works.play
		subject.replay += works.replay

	subjectThreads = []

	while len(subjectList) != 0:
		if len(threading.enumerate()) > MaxThreadCount:
			#time.sleep(1)
			pass
		else:
			subject = subjectList.pop()
			print(len(subjectList), subject.aid)
			t = SubjectThread(subject, endTime)
			subjectThreads.append(t)
			t.setDaemon(True)
			t.start()

	while len(threading.enumerate()) != 1:
		#time.sleep(1)
		pass

	for t in subjectThreads:
		subjectList.append(t.subject)


	from .. import hot
	hot.calSubjectScore(subjectList)
	subjectHistory = {}
	for subject in subjectList:
		subjectHistory[subject.aid] = subject.toSaveEsData()
	if not es.coverStatisticsDataReal('subject_history', subjectHistory):
		return False

	hot.calWorksScore(worksList)
	worksHistory = {}
	for works in worksList:
		worksHistory[works.vid] = works.toSaveEsData()
	return es.coverStatisticsDataReal('works_history', worksHistory)

			
def toWorks(worksInfo):
	if worksInfo.has_key('vid') or worksInfo.has_key('aid') or worksInfo.has_key('title'):
		return Works(worksInfo['vid'], worksInfo['aid'], worksInfo['title'], worksInfo['publishtime'], worksInfo['duration'] if worksInfo.has_key('duration') else 0)

#当天零点秒数
def getZeroTime():
	now = time.localtime(time.time())
	return time.mktime((now.tm_year, now.tm_mon, now.tm_mday, 0, 0, 0, 0, 0, 0))

#60天之前的毫秒数
def getDayBeforeTime(day):
	return (long(time.time()) - day * 24 * 60 * 60) * 1000

def cycleDisposePersonas():
	while True:
		try:
			disposePersonas()
		except Exception as error:
			print('Error: ' + str(error))
		gc.collect()
		time.sleep(600)

def disposePersonas():
	worksDict = readWorks()
	while True:
		endTime = disposePersonasOnce(worksDict)
		print('endTime: ' + str(endTime) + '(' + es.timeToEsLocalTime(endTime) + ')')
		if endTime > time.time() - 3600:
			break
		time.sleep(15)
		gc.collect()

def disposePersonasOnce(worksDict):
	startTime = readEndTime()
	hits = es.searchPersonas(startTime)

	userActions = {}
	worksActions = {}
	worksPlayers = {}

	aIndex = 0
	for index, hit in enumerate(hits):

		#if index % 100 == 0:
			#sys.stdout.write(str(index) + '\r')
			#sys.stdout.flush()

		source = hit['_source']
		uid = source['uid']
		createTime = es.esTimeToTime(source['create_time']) if source.has_key('create_time') else 0
		actions = source['body'].split('\n')

		for action in actions:
			try:
				items = action.split('\t')
				if len(items) > 2 and items[2].isdigit():
					_id = str(startTime) + '$' + str(aIndex)
					_time = es.timeToEsLocalTime(float(items[0]))
					addUserAction(userActions, _id, createTime, items[2], _time, uid, items)
					addWorksAction(worksDict, worksActions, _id, createTime, items[2], _time, uid, items)
					addWorksPlayer(worksPlayers, items[2], uid, items)
			except Exception as error:
				print('dispose personas action error: ' + str(error))
			aIndex += 1

		startTime = max(startTime, createTime)

	es.updateStatisticsData('user_actions', userActions)
	es.updateStatisticsData('works_actions', worksActions)
	es.updateStatisticsData('works_players', worksPlayers)
	writeEndTime(startTime)

	return startTime

def readEndTime():
	with open('endTime.ini', 'r') as f:
		return float(f.read())

def writeEndTime(endTime):
	with open('endTime.ini', 'w') as f:
		f.write(str(endTime))

def readWorks():
	worksDict = {}
	worksActions = {}
	for hit in es.scrollSearch('works_video_read', 'video', {"size":1000}):
		worksInfo = hit['_source']
		if worksInfo.has_key('vid') and worksInfo.has_key('aid') and worksInfo.has_key('publishtime') and worksInfo['publishtime'] != None:
			vid = worksInfo['vid']
			worksDict[vid] = worksInfo
			worksActions[vid] = {'time': es.timeToEsLocalTime(es.esTimeToTime(worksInfo['publishtime'], True)), 'vid': vid, 'aid': worksInfo['aid'], 'duration': worksInfo['duration'], 'action': 4, 'uid': worksInfo['publisheruid'] if worksInfo.has_key('publisheruid') else 0, 'value': 1}
	es.updateStatisticsData('works_actions', worksActions)
	return worksDict

'''
2: 打开推荐页
3: 推荐页点击
4: 推荐曝光
5: 打开老的订阅页
6: 打开播放页
7: 主动打开推荐页
8: 进入首页(公众号)
9: 进入首页(微信分享)
10: 进入首页(海报扫码)
11: 进入播放页(公众号)
12: 进入播放页(微信分享)
13: 进入播放页(海报扫码)
14: 微信版本号
'''

def addUserAction(userActions, _id, createTime, actionId, _time, uid, items):
	if actionId == '7' and items[1] == 'pages/common/index/index':
		action = 2 if len(items) >= 5 and items[4] == '1' else 5
		value = 1
	elif actionId == '7' and items[1] == 'pages/common/videoplay/videoplay':
		action = 6
		value = 1
	elif actionId == '9' and items[4] == '3':
		action = 4
		value = 1
	elif actionId == '15':
		action = 7
		value = 1
	elif actionId == '17' and items[1] in ['pages/common/index/index', 'pages/common/videoplay/videoplay'] and items[3] in ['1', '2', '3']:
		action = (7 if items[1] == 'pages/common/index/index' else 10) + int(items[3])
		value = 1
	elif actionId == '12':
		action = 14
		versionValueString = items[4].replace('.', '')
		value = int(versionValueString) if versionValueString.isdigit() else -1
	else:
		return
	userActions[_id] = {'createTime': createTime, 'time': _time, 'uid': uid, 'action': action, 'value': value}
	if actionId == '7' and items[1] == 'pages/common/videoplay/videoplay' and items[3] == '1' and len(items) >= 6 and items[5] == '4':
		userActions[_id + '$1'] = {'createTime': createTime, 'time': _time, 'uid': uid, 'action': 3, 'value': 1}

'''
1: 播放时长
2: 留存播放
3: 推荐曝光
4: 发布
5: 推荐点击
6: 播放页曝光
7: 播放页点击
8: 订阅页曝光
9: 订阅页点击
10: 主体页曝光
11: 主体页点击
12: 分享好友
13: 保存分享图片
14: 订阅
15: 取消订阅
16: 喜欢
17: 取消喜欢
'''
showMap = {'3': 3, '20': 6, '0': 8, '1': 10}
showPlayMap = {'4': 5, '1': 7, '2': 9, '3': 11}

simpleStatisticsMap = {'4': 12, '10': 14, '11': 15, '2': 16, '3': 17}

def addWorksAction(worksDict, worksActions, _id, createTime, actionId, _time, uid, items):
	if actionId == '6':
		vid = items[3]
		action = 1
		value = int(items[4])
	elif actionId == '9' and showMap.has_key(items[4]):
		vid = items[3]
		action = showMap[items[4]]
		value = 1
	elif actionId == '7' and items[1] == 'pages/common/videoplay/videoplay' and items[3] == '1' and len(items) >= 6 and showPlayMap.has_key(items[5]):
		vid = items[4]
		action = showPlayMap[items[5]]
		value = 1
	elif actionId == '5' and len(items) >= 5 and items[3] == '0':
		vid = items[4]
		action = 13
		value = 1
	elif simpleStatisticsMap.has_key(actionId):
		vid = items[4 if actionId in [10, 11] else 3]
		action = simpleStatisticsMap[actionId]
		value = 1
	else:
		return
	if not worksDict.has_key(vid):
		return
	worksInfo = worksDict[vid]
	worksActions[_id] = {'createTime': createTime, 'time': _time, 'vid': vid, 'aid': worksInfo['aid'], 'duration': worksInfo['duration'], 'action': action, 'uid': uid, 'value': value}
	if actionId == '6' and (value >= 60 or value >= 0.9 * worksInfo['duration']):
		worksActions[_id + '$1'] = {'createTime': createTime, 'time': _time, 'vid': vid, 'aid': worksInfo['aid'], 'duration': worksInfo['duration'], 'action': 2, 'uid': uid, 'value': 1}

def addWorksPlayer(worksPlayers, actionId, uid, items):
	if actionId == '1':
		worksPlayers[items[3] + '$' + str(uid)] = {'vid': items[3], 'uid': uid}




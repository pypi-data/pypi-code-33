#! /usr/bin/env python
# -*- coding: utf-8 -*-
import sys, time
from .. import es

SubjectIndexs = {
	"count": 0,
	"play": 1,
	"replay": 2,
	"conv": 3
}

WorksIndexs = {
	"play": 0,
	"like": 1,
	"shareF": 2,
	"shareI": 3,
	"replay": 4,
	"longTime": 5,
	"subAdd": 6,
	"playTimeAvg": 7,
	"conv": 8,
	"duration": 9,
	"size": 10
}

DurationSections = [0, 30, 60, 180, 300, 600, 900, 1200, 1800, 2400, 3600, 7200]


def createWorksArgsList(worksPersonas, aids=[], blackVids=[]):
	subjectDict, worksDict = createWorksDict(aids, blackVids)
	addBehaviors(subjectDict, worksDict, worksPersonas)
	return subjectDict, worksDict

def updateNewestActions(dau, worksPersonas):
	addActions(dau, worksPersonas, es.searchPersonas(worksPersonas.lastPersonasTime))

def addActions(dau, worksPersonas, personas):
	for index, hit in enumerate(personas):
		'''
		if index % 100 == 0:
			sys.stdout.write(str(index) + '\r')
			sys.stdout.flush()
		'''
		source = hit['_source']
		uid = source['uid']
		body = source['body']
		actions = body.split('\n')
		for action in actions:
			items = action.split('\t')
			if len(items) > 2 and items[2].isdigit():
				cTime = long(items[0])
				dau.addAction(uid, cTime)
				worksPersonas.addAction(uid, cTime, items[1], items[2], items[3:] if len(items) > 3 else [])
		if source.has_key('create_time'):
			worksPersonas.updateLastPersonasTime(source['create_time'])

def getDurationSectionsAvg(worksDict):
	length = len(DurationSections)
	durationSectionsInfo = []
	for index in range(length + 1):
		durationSectionsInfo.append([0, 0, 0])
	for works in worksDict.values():
		durationSectionsInfo[works['durationIndex']][0] += works['playTime']
		durationSectionsInfo[works['durationIndex']][1] += works['timeCount']
		durationSectionsInfo[works['durationIndex']][2] += 1
	durationSectionsAvg = []
	durationSectionsAvgCount = []
	for index in range(length + 1):
		timeCount = durationSectionsInfo[index][1]
		durationSectionsAvg.append(0 if timeCount == 0 else durationSectionsInfo[index][0] * 1.0 / timeCount)
		worksCount = durationSectionsInfo[index][2]
		durationSectionsAvgCount.append(0 if worksCount == 0 else timeCount)# * 1.0 / worksCount)
	return durationSectionsAvg, durationSectionsAvgCount

def addBehaviors(subjectDict, worksDict, worksPersonas):
	for behavior in worksPersonas.behaviors.values():
		vid = behavior['vid']
		if worksDict.has_key(vid):
			works = worksDict[vid]
			addBehavior(subjectDict[works['aid']], works, behavior)
	for subject in subjectDict.values():
		if subject['show'] > 0:
			subject['statis'][SubjectIndexs['conv']] = subject['showPlay'] * 1.0 / subject['show']

	durationSectionsAvg, durationSectionsAvgCount = getDurationSectionsAvg(worksDict)

	for works in worksDict.values():
		if works['playTime'] > 0 and works['timeCount'] > 0:
			works['statis'][WorksIndexs['playTimeAvg']] = works['playTime'] * 1.0 / works['timeCount'] / durationSectionsAvg[works['durationIndex']]
		if works['showPlay'] > 0 and works['show'] > 0:
			works['statis'][WorksIndexs['conv']] = works['showPlay'] * 1.0 / works['show']
		works['durationAvgPlay'] = durationSectionsAvgCount[works['durationIndex']]

def addBehavior(subject, works, behavior):
	if behavior['play'] > 0:
		works['statis'][WorksIndexs['play']] += 1
		subject['statis'][SubjectIndexs['play']] += 1
		if behavior['play'] > 1:
			works['statis'][WorksIndexs['replay']] += 1
			subject['statis'][SubjectIndexs['replay']] += 1
	if behavior['like']:
		works['statis'][WorksIndexs['like']] += 1
	if behavior['shareF'] > 0:
		works['statis'][WorksIndexs['shareF']] += 1
	if behavior['shareI'] > 0:
		works['statis'][WorksIndexs['shareI']] += 1

	if behavior['maxPlayTime'] > min(60, works['statis'][WorksIndexs['duration']] * 0.8):
		works['statis'][WorksIndexs['longTime']] += 1

	works['statis'][WorksIndexs['subAdd']] += behavior['subAdd']
	works['playTime'] += behavior['playTime']
	works['timeCount'] += behavior['timeCount']

	works['recShow'] += 1 if behavior['recShow'] > 0 else 0
	works['recShowPlay'] += 1 if behavior['recShowPlay'] > 0 else 0

	works['show'] += behavior['show']
	subject['show'] += behavior['show']
	showPlay = min(behavior['show'], behavior['showPlay'])
	works['showPlay'] += showPlay
	subject['showPlay'] += showPlay


def createWorksDict(aids=[], blackVids=[]):
	subjectDict = {}
	worksDict = {}
	for hit in es.scrollSearch('works_video_read', 'video', {"size":1000}):
		worksInfo = hit['_source']
		if not worksInfo.has_key('vid') or not worksInfo.has_key('aid') or (worksInfo.has_key('state') and worksInfo['state'] == 1) or (worksInfo.has_key('authorstate') and worksInfo['authorstate'] == 1):
			continue
		if not worksInfo.has_key('publishtime') or worksInfo['publishtime'] == None:
			continue
		publishTime = int(time.time() - es.esTimeToTime(worksInfo['publishtime'], True)) / 3600
		if publishTime > 336:
			continue
		aid = worksInfo['aid']
		vid = worksInfo['vid']
		if (len(aids) != 0 and not aid in aids) or vid in blackVids:
			continue
		if subjectDict.has_key(aid):
			subject = subjectDict[aid]
			subject['statis'][SubjectIndexs['count']] += 1
		else:
			subject = subjectDict[aid] = {'show': 0, 'showPlay': 0, 'statis': [1, 0, 0, 0]}
		duration = worksInfo['duration'] if worksInfo.has_key('duration') else 0
		size = worksInfo['filesize'] if worksInfo.has_key('filesize') else 0
		durationIndex = 12
		for index, value in enumerate(DurationSections):
			if duration < value:
				durationIndex = index
				break
		worksDict[vid] = {'title': worksInfo['title'], 'aid': aid, 'publishTime': publishTime, 'playCount': worksInfo['playcount'] if worksInfo.has_key('playcount') else 0, 'playTime': 0, 'timeCount': 0, 'show': 0, 'showPlay': 0, 'recShow': 0, 'recShowPlay': 0, 'durationIndex': durationIndex, 'durationAvgPlay': 0, 'statis': [0, 0, 0, 0, 0, 0, 0, 0, 0, duration, size]}

	return subjectDict, worksDict

'''

def writeWorksHot(esclient, index, worksHots):
	esclient.delete_by_query(index=index, doc_type='video', body={"query":{"match_all":{}}})
	doc = []
	for item in worksHots:
		doc.append({"index":{"_id":item[0]}})
		doc.append({"vid":item[0],"hot":item[1],"worksHot":item[2],"subjectHot":item[3],"timeDecay":item[4],"durationRate":item[5],"duration":item[6],"size":item[7],"publishTime":item[8],"playUserCount":item[9],"show":item[17],"showPlay":0 if item[17] == 0 else item[18] * 1.0 / item[17]})
	esclient.bulk(index=index, doc_type='video', body=doc)

def writeWorksBase(esclient, index, worksDict):


def createWorksList(isTest):
	subjectDict, worksDict = dealWithWorks(searchWorks(isTest))

	worksDict = updateHistoryWorks(isTest, worksDict)
	dau = getHistoryDau(isTest)
	
	worksDict, dau = dealWithPersonas(searchPersonas(isTest), worksDict, dau)

	return subjectDict, worksDict, dau

def updateHistoryWorks(isTest, worksDict):
	historyData = searchStatisticsData(isTest, 'statistics_works')
	for hit in historyData:
		vid = hit['_id']
		if worksDict.has_key(vid):
			worksDict[vid].update(hit['_source'])
		#TODO::后续要加上删除
	return worksDict
		
def getHistoryDau(isTest):
	dau = {}
	historyData = searchStatisticsData(isTest, 'statistics_dau')
	for hit in historyData:
		dau[hit['_id']] = hit['_source']['count']
	return dau

def toWriteWorksPersonas(action):
	


def dealWithWorks(works):
	subjectDict = {}
	worksDict = {}
	for hit in works:
		worksInfo = hit['_source']
		if not worksInfo.has_key('vid') or not worksInfo.has_key('aid'):
			continue
		if not subjectDict.has_key(worksInfo['aid']):
			subjectDict[worksInfo['aid']] = Subject(worksInfo['aid'])
		subject = subjectDict[worksInfo['aid']]
		works = worksDict[worksInfo['vid']] = Works(subject, worksInfo['vid'], worksInfo['duration'], 0, worksInfo['publishtime'])
		subject.addWorks(works)

	return subjectDict, worksDict

def dealWithPersonas(personas, worksDict, dau):
	now = time.localtime(time.time())
	zeroTime = time.mktime((now.tm_year, now.tm_mon, now.tm_mday, 0, 0, 0, 0, 0, 0))
	uids = [[], [], [], [], [], [], []]
	for index, hit in enumerate(personas):
		if index % 100 == 0:
			sys.stdout.write(str(index) + '\r')
    		sys.stdout.flush()
		uid = hit['_source']['uid']
		body = hit['_source']['body']
		actions = body.split('\n')
		for action in actions:
			items = action.split('\t')
			if len(items) > 2 and items[2].isdigit():

				calActive(uids, zeroTime, int(items[0]), uid)
				if items[2] in Works.DealFunc.keys():
					if items[2] == '7':
						if items[1] == 'pages/common/videoplay/videoplay' and len(items) >= 5 and items[3] == '1':
							vid = items[4]
							args = items[5:]
						else:
							continue
					elif items[2] == '10' or items[2] == '11':
						vid = items[4] if len(items) > 4 else ''
						if vid == '':
							continue
					else:
						vid = items[3]
						args = items[4:]
					if worksDict.has_key(vid):
						worksDict[vid].addAction(items[2], uid, args)

	dau = []
	for dayUids in  uids:
		dau.append(len(dayUids))
	return worksDict, dau


def calActive(uids, zeroTime, actionTime, uid):
	for day in range(7):
		if actionTime >= (zeroTime - oneDay * day) and not uid in uids[day]:
			uids[day].append(uid)
			return

def scrollSearch(isTest, index, doc_type, body):
	esclient = testEsclient if isTest else relEsclient
	hits = []
	result = esclient.search(index=index, doc_type=doc_type, scroll='1m', body=body)
	while len(result['hits']['hits']) != 0:
		hits.extend(result['hits']['hits'])
		scroll_id = result['_scroll_id']
		result = esclient.scroll(scroll_id=scroll_id, scroll='1m')
	return hits


def searchStatisticsData(isTest, index)
	body = {
		"size": 1000
	}
	return scrollSearch(isTest, index, 'test' if isTest else 'rel', body)


def searchWorks(isTest):
	body = {
		"size": 1000
	}
	return scrollSearch(isTest, 'works_video_read', 'video', body)




def write(filename, itemDict):
	doubleArray = []
	for item in itemDict.values():
		doubleArray.append(item.getArgs())
	with open(filename, 'w') as f:
		data = []
		for itemArray in doubleArray:
			data.append('\t'.join(map(str, itemArray)))
		f.write('\n'.join(data))
'''



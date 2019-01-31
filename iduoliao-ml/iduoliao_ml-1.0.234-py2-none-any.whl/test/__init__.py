#! /usr/bin/env python
# -*- coding: utf-8 -*-

import time, gc
from .. import es, dataDispose, imatrix
from numpy import *

def test():
	'''
	ab = mat([[1, 2, 3, 4], [0.3, 3, 4, 0.1], [3, 1, 3, 5], [10, 3, 100, 30], [9, 30, 40, 99], [99, 65, 0, 39]])
	print(ab)
	print('----------')
	print(imatrix.inOneDiv(ab))
	print('----------')
	print(imatrix.inOneDivOffStray(ab))
	'''
	recordEsToRedis()
	#hotGrow()
	'''
	l = [[1]]
	for i in range(0, 5000):
		l.append([0.0001])
	for i in range(0, 5000):
		l.append([0.0002])
	print(imatrix.inOne(mat(l)))
	'''

def recordEsToRedis():
	currentUid = readEndUid()
	index = 0
	while True:
		nextUids = es.getAllUids(currentUid)
		if len(nextUids) == 0:
			break
		for nextUid in nextUids:
			hitInts = []
			existInts = es.getIntsByUid(nextUid)
			hits = es.scrollSearch('statistics_works_hot_fixed_backups', 'recommendviewrecordsearch', {"query":{"bool":{"must":[{"range":{"time":{"lte":1548921600000}}},{"term":{"uid":{"value":nextUid}}}]}},"size":10000})
			for hit in hits:
				i = es.getIntByVid(hit['_parent'])
				if i != None and i not in existInts:
					hitInts.append(str(i))
			index += 1
			print(index, nextUid, len(hitInts))
			es.writeIntsByUid(nextUid, hitInts)
			writeEndUid(nextUid)
			writeUids(nextUid)
			currentUid = nextUid
		gc.collect()
	
def readEndUid():
	with open('endUid.ini', 'r') as f:
		return long(f.read())

def writeEndUid(uid):
	with open('endUid.ini', 'w') as f:
		f.write(str(uid))

def writeUids(uid):
	with open('uids', 'a') as f:
		f.write('{"uid":' + str(uid) + ',"r1size":8,"r2size":2}\n')

def hotGrow():
	for vid in ["8133878fd33659cd57fac322e6e08e53", "b9ee6b64790042a3de02b430edd359c1", "2cdef127c294230a2d86438a79c4db3f", "54423e3437395068981e503ec646e682", "c9c2ad4ab7c4c3680e7d0ef5b0c909c9", "ab68fbda808b6c5ab1c84e43c3a1aedc", "a39f8db3de774426e5500b468adcd3b0"]:
		growDict = {}
		for i in range(0, 1000):
			endTime = 1547568000 + i * 10 * 60
			print(vid, endTime)
			works = dataDispose.createWorks(vid)
			works.updateActions(endTime)
			data = works.toSaveEsData()
			data['conv'] = 0 if works.resShow <= 0 else works.resShowPlay * 1.0 / works.resShow
			data['likeRatio'] = 0 if works.play <= 0 else works.like * 1.0 / works.play
			data['shareRatio'] = 0 if works.play <= 0 else works.share * 1.0 / works.play
			data['longPlayRatio'] = 0 if works.play <= 0 else works.longPlay * 1.0 / works.play
			data['subRatio'] = 0 if works.play <= 0 else works.sub * 1.0 / works.play
			growDict[vid + '$' + str(endTime)] = data
		es.updateStatisticsData('works_hot_grow', growDict)

def statisticsRecConv():
	convTotal = 0
	uids = []
	for hit in es.searchStatisticsDataByBody('works_actions', {"query": {"bool": {"must": [{"range": {"time": {"gte": 1547049600000, "lt": 1547136000000}}}, {"term": {"action": {"value": 3}}}]}}, "size":10000}):
		uid = hit["_source"]["uid"]
		if uid in uids:
			continue
		uids.append(uid)
		body = {"query": {"bool": {"must": [{"term": {"uid": uid}}, {"terms": {"action": [3, 5]}}, {"range": {"time": {"gte": 1547049600000, "lt": 1547136000000}}}]}}, "size": 0, "aggs": {}}
		body['aggs']['vid_diff'] = {"terms": {"field": "action", "size": 2}, "aggs": {"count": {"cardinality": {"field": "vid"}}}}
		aggs = es.searchStatisticsAggs('works_actions', body)
		recShow = 0
		recShowPlay = 0
		for bucket in aggs['vid_diff']['buckets']:
			if bucket['key'] == 3:
				recShow = bucket['count']['value']
			elif bucket['key'] == 5:
				recShowPlay = bucket['count']['value']
		convTotal += (0 if recShow == 0 else recShowPlay * 1.0 / recShow)
		count = len(uids)
		print(count, uid, recShow, recShowPlay, convTotal, convTotal * 1.0 / count)
		time.sleep(1)



def testA():
	worksList = dataDispose.getWorksList()
	data = {}
	for index, works in enumerate(worksList):
		print(index, works.vid)
		body = {"query": {"bool": {"must": [{"term": {"vid": works.vid}}, {"terms": {"action": [3, 5]}}]}}, "size": 0, "aggs": {}}
		body['aggs']['uid_diff'] = {"terms": {"field": "action", "size": 2}, "aggs": {"count": {"cardinality": {"field": "uid"}}}}
		aggs = es.searchStatisticsAggs('works_actions', body)
		data[works.vid] = {'vid': works.vid, 'aid': works.aid, 'title': works.title, 'resShow': 0, 'resShowPlay': 0}
		for bucket in aggs['uid_diff']['buckets']:
			if bucket['key'] == 3:
				data[works.vid]['resShow'] = bucket['count']['value']
			elif bucket['key'] == 5:
				data[works.vid]['resShowPlay'] = bucket['count']['value']

	#print(data)
	es.updateStatisticsData('works_info', data)


	'''
	values = []
	for key, value in {'a': 1, 'b': 2}.items():
		values += [key, value]
	testArgs(**{'a': 1, 'b': 2})
	'''
	'''
	es.setEnv(False)
	hits = es.searchStatisticsDataByBody('works_actions', {"query": {"term": {"vid": "ecbf3aa1599e140896e0f6c241d93681"}}, "size": 10000})
	
	dataDict = {}
	for hit in hits:
		dataDict[hit['_id']] = hit['_source']

	es.setEnv(True)
	es.updateStatisticsData('works_actions', dataDict)
	'''

def testArgs(*args, **kwargs):
	print(args)
	print(kwargs)
#! /usr/bin/env python
# -*- coding: utf-8 -*-

import time, random, math
from .. import es
from bftWorks import BftWorks

def updateWorks():
	#endTime = int(time.time())
	lastCheckTime = 1547568000

	endTime = 1547568000
	vids = []
	for index in range(0, 80):
		vids.append(str(index))
	worksDict = getWorksDict(vids, endTime)

	while True:
		if random.randint(1, 2) == 1:
			vids.append(str(time.time()))
		worksDict = updateWorksDict(worksDict, vids, endTime)
		endTime = update(worksDict, endTime)
		
		if endTime - lastCheckTime >= 24 * 60 * 60:
			dailyCheck(worksDict, lastCheckTime)
			lastCheckTime = endTime

		saveWorksToEs(worksDict)

		saveRecord(worksDict, endTime)

		print(es.timeToEsLocalTime(endTime))
		time.sleep(30)

def update(worksDict, startTime):
	#endTime = int(time.time() - 90)
	endTime = startTime + 10 * 60
	for hit in es.searchStatisticsDataByBody("works_actions", {"query": {"bool": {"must": [{"range": {"time": {"gte": startTime * 1000, "lt": endTime * 1000}}}, {"terms": {"action": [2, 3, 5, 12, 13, 16]}}]}}, "size": 10000}):
		action = hit['_source']
		vid = action['vid']
		if random.randint(1, 5) == 1:
			for i in range(0, 100):
				vid = random.sample(worksDict.keys(), 1)[0]
				if worksDict[vid].pool in [BftWorks.Pools['FlowFirst'], BftWorks.Pools['FlowSecond'], BftWorks.Pools['FlowThird']]:
					break
		if worksDict.has_key(vid):
			worksDict[vid].updateAction(action)

	for works in worksDict.values():
		works.updateStatus()

	return endTime

def updateWorksDict(worksDict, vids, endTime):
	newWorksDict = {}
	for vid in vids:
		if worksDict.has_key(vid):
			newWorksDict[vid] = worksDict[vid]
		else:
			works = BftWorks(vid)
			works.updateHistoryActions(endTime)
			newWorksDict[vid] = works
	return newWorksDict

def getWorksDict(vids, endTime):
	worksDict = {}
	for vid in vids:
		worksDict[vid] = BftWorks(vid)
	syncEsWorks(worksDict)
	for works in worksDict.values():
		works.updateHistoryActions(endTime)
	return worksDict

def dailyCheck(worksDict, lastCheckTime):
	awaitWorks = [[], [], []]
	riseCounts = [0, 0, 0]

	for works in worksDict.values():
		if works.status == BftWorks.Status['Await']:
			awaitWorks[works.getPool()].append(works)
		if works.status != BftWorks.Status['Fail']:
			for record in works.records:
				if record['time'] > lastCheckTime:
					riseCounts[works.getPool()] += 1

	for index, worksList in enumerate(awaitWorks):
		worksList.sort(reverse=True, key=lambda item: item.score)

		riseCount = riseCounts[index]
		polishCount = (len(worksList) + riseCount) * 0.2 - riseCount

		for index, works in enumerate(worksList):
			if index < polishCount - 1:
				works.rise(2)
			elif works.isResurgence():
				works.fail()
			else:
				works.resurgence()

def saveRecord(worksDict, endTime):
	record = {'time': es.timeToEsLocalTime(endTime), 'flowFirstCount': 0, 'flowSecondCount': 0, 'flowThirdCount': 0, 'successCount': 0, 'failCount': 0}
	for works in worksDict.values():
		if works.status == BftWorks.Status['Normal']:
			record[{0: 'flowFirstCount', 1: 'flowSecondCount', 2: 'flowThirdCount'}[works.getPool()]] += 1
		elif works.status == BftWorks.Status['Success']:
			record['successCount'] += 1
		elif works.status in [BftWorks.Status['Await'], BftWorks.Status['Fail']]:
			record['failCount'] += 1
	return es.updateStatisticsData('works_filter_pool_record', {int(endTime): record})

def syncEsWorks(worksDict):
	for hit in es.searchStatisticsData('works_filter_pool'):
		vid = hit['_id']
		if worksDict.has_key(vid):
			worksDict[vid].syncEsData(hit['_source'])

def saveWorksToEs(worksDict):
	worksData = {}
	for vid, works in worksDict.items():
		worksData[vid] = works.toSaveEsData()
	es.updateStatisticsData('works_filter_pool', worksData)

	
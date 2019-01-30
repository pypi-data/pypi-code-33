#! /usr/bin/env python
# -*- coding: utf-8 -*-

from .. import es

def clickCF():
	worksInfos = {}

	uidWorks = {}
	hits = es.searchStatisticsDataByBody('works_actions', {"query": {"terms": {"action": [3, 5]}},"size": 10000})
	for hit in hits:
		source = hit['_source']
		uid = source['uid']
		vid = source['vid']
		if uidWorks.has_key(uid):
			pass 

def cf():
	worksInfos = {}

	uidWorks = {}
	hits = es.searchStatisticsDataByBody('works_actions', {"query": {"match": {"action": 2}},"size": 10000})
	for hit in hits:
		source = hit['_source']
		uid = source['uid']
		vid = source['vid']
		if uidWorks.has_key(uid):
			vids = uidWorks[uid]
			if vids.count(vid) != 0:
				continue
		else:
			vids = uidWorks[uid] = []

		worksInfo = getWorksInfo(worksInfos, vid)
		worksInfo['count'] += 1
		for sVid in vids:
			addSimilar(worksInfo, sVid)
			#addSimilar(getWorksInfo(worksInfos, sVid), vid)

		vids.append(vid)

	saveSimilars(worksInfos)

def saveSimilars(worksInfos):
	allSimilars = {}
	for vid, info in worksInfos.items():
		similars = info['similars']
		for sVid, value in similars.items():
			allSimilars[vid + '$' + sVid] = {'vidA': vid, 'vidB': sVid, 'value': value * 1.0 / info['count'] / worksInfos[sVid]['count']}
	es.updateStatisticsData('works_similar', allSimilars)

def getWorksInfo(worksInfos, vid):
	if not worksInfos.has_key(vid):
		worksInfos[vid] = {'count': 0, 'similars': {}}
	return worksInfos[vid]

def addSimilar(worksInfo, sVid):
	similars = worksInfo['similars']
	if similars.has_key(sVid):
		similars[sVid] += 1
	else:
		similars[sVid] = 1





#! /usr/bin/env python
# -*- coding: utf-8 -*-

def updateHistoryData(whiteAids=[], blackVids=[]):
	subjectDict, worksDict = createWorksDict(aids, blackVids)

def getWorksActionInfo(vid):
	worksInfo = {}



# return
# subjectDict: aid subject(count:作品数量)
# worksDict: vid works(duration:时长 title:标题 aid:认证号id publishTime:发布时间 score:分数)
def createWorksDict(whiteAids=[], blackVids=[]):
	subjectDict = {}
	worksDict = {}
	for hit in es.scrollSearch('works_video_read', 'video', {"size":1000}):
		worksInfo = hit['_source']
		if not worksInfo.has_key('vid') or not worksInfo.has_key('aid') or (worksInfo.has_key('state') and worksInfo['state'] == 1) or (worksInfo.has_key('authorstate') and worksInfo['authorstate'] == 1):
			continue
		if not worksInfo.has_key('publishtime') or worksInfo['publishtime'] == None:
			continue
		publishTime = int(time.time() - es.esTimeToTime(worksInfo['publishtime'], True)) / 3600
		if publishTime > 10000:
			continue
		aid = worksInfo['aid']
		vid = worksInfo['vid']
		if (len(aids) != 0 and not aid in aids) or vid in blackVids:
			continue
		if subjectDict.has_key(aid):
			subject = subjectDict[aid]
			subject['count'] += 1
		else:
			subject = subjectDict[aid] = {'count': 1}
		duration = worksInfo['duration'] if worksInfo.has_key('duration') else 0
		durationIndex = 12
		for index, value in enumerate(DurationSections):
			if duration < value:
				durationIndex = index
				break
		worksDict[vid] = {'title': worksInfo['title'], 'aid': aid, 'publishTime': publishTime, 'playCount': worksInfo['playcount'] if worksInfo.has_key('playcount') else 0, 'playTime': 0, 'timeCount': 0, 'show': 0, 'showPlay': 0, 'recShow': 0, 'recShowPlay': 0, 'durationIndex': durationIndex, 'durationAvgPlay': 0, 'statis': [0, 0, 0, 0, 0, 0, 0, 0, 0, duration, size]}

	return subjectDict, worksDict


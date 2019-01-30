#! /usr/bin/env python
# -*- coding: utf-8 -*-

import math
from .. import imatrix
from numpy import *

#TODO:存了两份 考虑怎么合并
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

SubjectTotalWeight = 0.3

SubjectWeight = {
	'count': 20,
	'play': 1,
	'replay': 5
}

WorksWeight = {
	'play': 1,
	'like': 10,
	'shareF': 15,
	'shareI': 20,
	'replay': 5,
	'longTime': 10,
	'subAdd': 20
}

TimeDecay = {
	'half': 168,
	'flutter': 48.0
}

SameAidDecay = 0.0

def calSubjectScore(subjectList):
	subjectArgs = []
	for subject in subjectList:
		subjectArgs.append([subject.count, subject.play, subject.replay])
	subjectMat = imatrix.inOne(mat(subjectArgs))

	for index, subject in enumerate(subjectList):
		subject.score = (subjectMat[index, 0] * SubjectWeight['count'] + subjectMat[index, 1] * SubjectWeight['play'] + subjectMat[index, 2] * SubjectWeight['replay']) * subject.conv

def calWorksScore(worksList, dauFactor=10):
	if len(worksList) == 0:
		return

	worksArgs = []
	worksDurationTimeAvg = {}
	worksDurationPlay = {}
	for works in worksList:
		worksArgs.append([works.play, works.like, works.shareF, works.shareI, works.replay, works.longPlay, works.sub])
		if worksDurationTimeAvg.has_key(works.durationIndex):
			worksDurationTimeAvg[works.durationIndex] += works.timeAvg
			worksDurationPlay[works.durationIndex] += works.play
		else:
			worksDurationTimeAvg[works.durationIndex] = works.timeAvg
			worksDurationPlay[works.durationIndex] = works.play
	worksMat = imatrix.inOne(mat(worksArgs))
	worksMatTwo = imatrix.inOneDiv(hstack((worksMat[:, 0] * WorksWeight['play'] + worksMat[:, 1] * WorksWeight['like'] + worksMat[:, 2] * WorksWeight['shareF'] + worksMat[:, 3] * WorksWeight['shareI'] + worksMat[:, 4] * WorksWeight['replay'], worksMat[:, 5] * WorksWeight['longTime'] + worksMat[:, 6] * WorksWeight['subAdd'])))
	worksMatFinal = imatrix.inOneDiv(worksMatTwo[:, 0] * (11 - dauFactor) + worksMatTwo[:, 1] * dauFactor)

	for index, works in enumerate(worksList):
		works.score = worksMatFinal[index, 0]
		works.ratio = worksDurationPlay[works.durationIndex]

def updateWeight(weight):
	global SubjectTotalWeight, SubjectWeight, WorksWeight, TimeDecay, SameAidDecay
	SubjectTotalWeight = weight['subjectTotal']
	SubjectWeight = weight['subject']
	WorksWeight = weight['works']
	TimeDecay = weight['timeDecay']
	SameAidDecay = weight['sameAidDecay'] if weight.has_key('sameAidDecay') else 0.0	

def calHotV2(subjectHistory, worksHistory, worksList, dauFactor, aidWeights, vidWeights):
	calWorksScore(worksList, 11 - dauFactor)

	baseHot = []
	for works in worksList:
		vid = works.vid
		aid = works.aid
		baseHot.append([subjectHistory[aid]['score'] * worksHistory[vid]['ratio'] if subjectHistory.has_key(aid) and worksHistory.has_key(vid) else 0])

	baseHotMat = imatrix.inOneDiv(mat(baseHot))

	hotList = {}
	for index, works in enumerate(worksList):
		vid = works.vid
		aid = works.aid
		actionHot = (works.score + (worksHistory[vid]['score'] if worksHistory.has_key(vid) else 0)) / 2
		if vidWeights.has_key(vid):
			weight = float(vidWeights[vid])
		elif aidWeights.has_key(int(aid)):
			weight = float(aidWeights[int(aid)])
		else:
			weight = 1
		hotList[vid] = {'vid': vid, 'aid': aid, 'title': works.title, 'hot': (baseHotMat[index, 0] * SubjectTotalWeight + actionHot) * getDecayRatio(works.publishTime) * weight * 100000, 'isNew': works.publishTime < 72}

	hotListFinal = {}
	for index, item in enumerate(sorted(hotList.items(), key=lambda x: x[1]['hot'], reverse=True)):
		item[1]['ranking'] = index + 1
		hotListFinal[item[0]] = item[1]

	return hotListFinal











def calHot(dauFactor, newShowMax, subjectDict, worksDict):
	subjectAids, subjectHotMat = calSubjectHot(subjectDict)
	worksVids, worksAids, worksHotMat, worksRate = calWorksHot(worksDict, dauFactor, newShowMax)

	shArray = []
	for index, aid in enumerate(worksAids):
		shArray.append([subjectHotMat[subjectAids.index(aid), 0] * worksDict[worksVids[index]]['durationAvgPlay']])

	shm = imatrix.inOneDiv(mat(shArray))
	whm = imatrix.inOneDiv(worksHotMat)

	#worksNew = {}
	for index, vid in enumerate(worksVids):
		baseHot = shm[index, 0] * SubjectTotalWeight #* len(subjectDict) / len(worksDict)
		actionHot = whm[index, 0]

		works = worksDict[vid]

		decayRatio = getDecayRatio(works['publishTime'])

		works['vid'] = vid
		works['totalHot'] = (baseHot + actionHot) * decayRatio
		works['baseHot'] = baseHot
		works['actionHot'] = actionHot
		works['decayRatio'] = decayRatio
		works['baseRate'] = worksRate[index, 0]

		works['isNew'] = works['publishTime'] < 72 and works['show'] <= newShowMax

	mHotList = {}
	aidDecays = {}
	for item in sorted(worksDict.items(), key=lambda x: x[1]['totalHot'], reverse=True):
		if index >= 50000:
			break
		works = item[1]
		aid = works['aid']
		if aidDecays.has_key(aid) and aidDecays[aid] < 0.25:
			aidDecays[aid] += SameAidDecay
		else:
			aidDecays[aid] = 0
		works['hot'] = int((1 - aidDecays[aid]) * works['totalHot'] * 100000) + calLowerBound(works['recShowPlay'], works['recShow'])
		mHotList[item[0]] = works

	hotList = {}
	for index, item in enumerate(sorted(mHotList.items(), key=lambda x: x[1]['hot'], reverse=True)):
		item[1]['ranking'] = index + 1
		hotList[item[0]] = item[1]
		'''
		for i in range(500):
			info = item[1].copy()
			info['vid'] = item[0] + str(i)
			hotList[item[0] + str(i)] = info
		'''

	#if hotList.has_key('5fe50cdd8028734584f0832d5338bfe5'):
	#	hotList['5fe50cdd8028734584f0832d5338bfe5']['hot'] = 200000

	return hotList

def calLowerBound(pos, n):
	if n == 0:
		return 0
	z = 1.96
	pos = min(pos, n)
	phat = 1.0 * pos / n
	return (phat + z * z/(2 * n)  -  z * math.sqrt((phat * (1 - phat) + z * z/(4 * n)) / n))/(1 + z * z / n)

def calSubjectHot(subjectDict):
	subjectAids = []
	subjectArgs = []
	for aid, subject in subjectDict.items():
		subjectAids.append(aid)
		subjectArgs.append(subject['statis'])
	subjectMat = imatrix.inOne(mat(subjectArgs))
	subjectHotMat = multiply((subjectMat[:, SubjectIndexs['count']] * SubjectWeight['count'] + subjectMat[:, SubjectIndexs['play']] * SubjectWeight['play'] + subjectMat[:, SubjectIndexs['replay']] * SubjectWeight['replay']), subjectMat[:, SubjectIndexs['conv']])
	return subjectAids, subjectHotMat

def calWorksHot(worksDict, dauFactor, newShowMax):
	worksVids = []
	worksAids = []
	worksArgs = []
	worksForceCredible = []
	for vid, works in worksDict.items():
		worksVids.append(vid)
		worksAids.append(works['aid'])
		worksArgs.append(works['statis'])
		worksForceCredible.append([1 if works['show'] > newShowMax else 0])
	worksMat = mat(worksArgs)
	worksBaseMat = imatrix.inOne(worksMat[:, [WorksIndexs['play'], WorksIndexs['like'], WorksIndexs['shareF'], WorksIndexs['shareI'], WorksIndexs['replay'], WorksIndexs['longTime'], WorksIndexs['subAdd']]])

	worksActionMat = worksBaseMat[:, WorksIndexs['play']] * WorksWeight['play'] + worksBaseMat[:, WorksIndexs['like']] * WorksWeight['like'] + worksBaseMat[:, WorksIndexs['shareF']] * WorksWeight['shareF'] + worksBaseMat[:, WorksIndexs['shareI']] * WorksWeight['shareI'] + worksBaseMat[:, WorksIndexs['replay']] * WorksWeight['replay']
	worksForceMat = multiply(multiply(multiply(worksBaseMat[:, WorksIndexs['longTime']] * WorksWeight['longTime'] + worksBaseMat[:, WorksIndexs['subAdd']] * WorksWeight['subAdd'], worksMat[:, WorksIndexs['playTimeAvg']]), worksMat[:, WorksIndexs['conv']]), mat(worksForceCredible))

	return worksVids, worksAids, worksActionMat * dauFactor + worksForceMat * (11 - dauFactor), getWorksRate(worksMat[:, [WorksIndexs['duration'], WorksIndexs['play']]])

def getDecayRatio(publishTime):
	return 1 - 1 / (1 + math.exp((TimeDecay['half'] - publishTime) / TimeDecay['flutter']))

def getWorksRate(mat):
	#TODO::目前还没有统计size
	total = mat[:,1].sum(axis=0)[0,0]
	avg = multiply(mat[:,0], mat[:,1]).sum(axis=0)[0,0] / total
	vari = sqrt(multiply(square(mat[:,0] - avg), mat[:,1]).sum(axis=0)[0,0] / total)
	return exp(-square(mat[:,0] - avg) / 2 / square(vari)) * (1 / math.sqrt(2 * math.pi) / vari)

'''

def calHot(subjectDict, worksDict, dau):
	worksVid = []
	worksAid = []
	matArray = []
	timeArray = []
	changeArray = []
	worksTotalTime = 0
	worksTimeCount = 0
	durationArray = []
	for works in worksDict.values():
		worksVid.append(works.vid)
		worksAid.append(works.subject.aid)
		matArray.append([len(works.playUids), works.like, len(works.shareFUids), len(works.shareIUids), len(works.replyPlayUids), len(works.longTimeUids), works.subAdd])
		timeArray.append([0 if works.timeCount == 0 else works.totalTime * 1.0 / works.timeCount])
		changeArray.append([0 if works.show == 0 else works.showPlay * 1.0 / works.show])
		worksTotalTime += works.totalTime
		worksTimeCount += works.timeCount
		durationArray.append([works.duration, len(works.playUids)])

	durationMat = mat(durationArray)
	durationTotal = durationMat[:,1].sum(axis=0)[0,0]
	durationAvg = multiply(durationMat[:,0], durationMat[:,1]).sum(axis=0)[0,0] / durationTotal
	durationVari = sqrt(multiply(square(durationMat[:,0] - durationAvg), durationMat[:,1]).sum(axis=0)[0,0] / durationTotal)
	durationRate = exp(-square(durationMat[:,0] - durationAvg) / 2 / square(durationVari)) * (1 / math.sqrt(2 * math.pi) / durationVari)
	#print(concatenate([durationRate, durationMat[:,0]], axis=1))

	worksTimeAvg = worksTotalTime * 1.0 / worksTimeCount

	timeMat = mat(timeArray) / worksTimeAvg
	changeMat = mat(changeArray)
	worksArgsMat = imatrix.inOne(mat(matArray))

	worksMat = mat(zeros((len(matArray), 3)))
	worksMat[:, 0] = worksArgsMat[:, 0] * 1 + worksArgsMat[:, 1] * 5 + worksArgsMat[:, 2] * 10 + worksArgsMat[:, 3] * 15 + worksArgsMat[:, 4] * 5
	worksMat[:, 1] = multiply(multiply(worksArgsMat[:, 5] * 10 + worksArgsMat[:, 6] * 20, timeMat), changeMat)

	rate = 0
	for index in range(1, 5):
		rate += (dau[index] - dau[index + 1]) * 1.0 / dau[index + 1]
	activeDiv = dau[1] * (1 + rate / 5) * 0.4
	a = 1 / (5.5 * activeDiv)
	factor = min(10, max(1, 1 / (a * dau[0])))

	worksMat = imatrix.inOne(worksMat)
	worksMatFinal = worksMat[:, 0] * factor + worksMat[:, 1] * (11 - factor)
	worksMatFinalOne = imatrix.inOne(worksMatFinal)

	subjectAids = []
	subjectArray = []
	for subject in subjectDict.values():
		subjectAids.append(subject.aid)
		subjectArray.append(subject.getArgs()[1:])

	subjectMat = mat(subjectArray)
	subjectMatOne = imatrix.inOne(subjectMat)

	subjectMatFinal = multiply((subjectMatOne[:, 0] * 20 + subjectMatOne[:, 1] * 1 + subjectMatOne[:, 2] * 5), subjectMat[:, 3]) * durationRate[index, 0]
	subjectMatFinalOne = imatrix.inOne(subjectMatFinal)

	worksHots = []
	for index, aid in enumerate(worksAid):
		worksInfo = []
		worksInfo.append(worksVid[index])
		worksInfo.append((worksMatFinalOne[index, 0] + subjectMatFinalOne[subjectAids.index(aid), 0] * 0.3) * worksDict[worksVid[index]].getDecayRatio())
		worksInfo.append(worksMatFinalOne[index, 0])
		worksInfo.append(subjectMatFinalOne[subjectAids.index(aid), 0])
		worksInfo.append(worksDict[worksVid[index]].getDecayRatio())
		worksInfo.append(durationRate[index, 0])
		worksInfo = worksInfo + worksDict[worksVid[index]].getArgs()[1:]
		worksHots.append(worksInfo)
	print(len(worksHots))
	return worksHots

	'''
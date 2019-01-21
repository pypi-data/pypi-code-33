#! /usr/bin/env python
# -*- coding: utf-8 -*-

import time, gc, sys
from .. import es

reload(sys)
sys.setdefaultencoding('utf-8')

def cycleSave():
	while True:
		#try:
		save()
		#except Exception as error:
		#	print('Error: ' + str(error))
		gc.collect()
		time.sleep(600)

def save():
	while True:
		endTime = saveOnce()
		print('endTime: ' + str(endTime) + '(' + es.timeToEsLocalTime(endTime) + ')')
		if endTime > time.time() - 3600:
			break
		time.sleep(5)
		gc.collect()

def saveOnce():
	startTime = readEndTime()
	hits = es.searchPersonas(startTime)

	dataDict = {}

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
					actionTime = time.localtime(float(items[0]))
					key = '-'.join([items[2], str(actionTime.tm_year), str(actionTime.tm_mon)])
					if not dataDict.has_key(key):
						dataDict[key] = []
					dataDict[key].append(action)
				'''
				if len(items) > 2 and items[2].isdigit() and items[2] == '18' and len(items) >= 7:
					if items[3] not in ['https://cdn.img1.iduoliao.cn', 'https://cdn.media.iduoliao.cn']:
						continue
					dataDict[str(startTime) + '$' + str(aIndex)] = {'time': es.timeToEsLocalTime(float(items[0])), 'uid': uid, 'type': items[5], 'delay': long(items[6]), 'vid': items[4], 'domain': items[3]}
				'''
			except Exception as error:
				print('dispose personas action error: ' + str(error))
			aIndex += 1

		startTime = max(startTime, createTime)

	#es.updateStatisticsData('works_kartuns', dataDict)
	for key, lines in dataDict.items():
		with open('actions/' + key, 'a') as f:
			f.write('\n'.join(lines) + '\n')
	writeEndTime(startTime)

	return startTime

def readEndTime():
	with open('endTime.ini', 'r') as f:
		return float(f.read())

def writeEndTime(endTime):
	with open('endTime.ini', 'w') as f:
		f.write(str(endTime))
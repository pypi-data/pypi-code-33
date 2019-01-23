#! /usr/bin/env python
# -*- coding: utf-8 -*-

import time, gc, sys, json
from .. import es

reload(sys)
sys.setdefaultencoding('utf-8')

def cycleSave():
	while True:
		try:
			save()
		except Exception as error:
			print('Error: ' + str(error))
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
	kartunDict = {}

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
					dataDict[key].append('\t'.join([str(uid), time.strftime('%Y-%m-%d %H:%M:%S', actionTime)] + items[1:]))
				if len(items) > 2 and items[2].isdigit() and items[2] == '18' and len(items) >= 7:
					if items[3] not in ['https://cdn.img1.iduoliao.cn', 'https://cdn.media.iduoliao.cn']:
						continue
					kartunDict[str(startTime) + '$' + str(aIndex)] = {'time': es.timeToEsLocalTime(float(items[0])), 'uid': uid, 'type': items[5], 'delay': long(items[6]), 'vid': items[4], 'domain': items[3]}
			except Exception as error:
				print('dispose personas action error: ' + str(error))
			aIndex += 1

		startTime = max(startTime, createTime)

	es.updateStatisticsData('works_kartuns', kartunDict)
	for key, lines in dataDict.items():
		with open('actions/' + key, 'a') as f:
			f.write('\n'.join(lines) + '\n')

	saveErrorAvplay(int(readEndTime() * 1000), int(startTime * 1000))

	writeEndTime(startTime)

	return startTime

def saveErrorAvplay(start, end):
	esData = {}
	count = 0
	for hit in es.scrollSearch('clientlog_read', 'watch', {"size": 10000, "query": {"bool": {"must": [{"range": {"create_time": {"gte": start,"lt": end}}}, {"term": {"type": {"value": "avplay"}}}]}}}):
		source = hit['_source']
		body = source['body'].encode('utf-8').replace('\t', ' ')
		for index, item in enumerate(body.split('\n')):
			start = item.find('{')
			if start == -1:
				if item.strip() != '':
					print(item)
					count += 1
				continue
			try:
				data = json.loads(item[start:])
				endtime = int(es.esTimeToTime(source['endtime']))
				data['time'] = es.timeToEsLocalTime(endtime)
				esData[data['uid'] + '$' + str(endtime) + '$' + str(index)] = data
			except Exception as error:
				print(item[start:], error)
				count += 1
			#lines.append('\t'.join([str(int(es.esTimeToTime(source['endtime']))), data['uid'], data['nick'], data['vid'], data['ym_version'], data['wx_version'], data['model'], data['networktype'], data['platform'], data['sdkversion'], str(data['width'] if data.has_key('width') else -1), str(data['height'] if data.has_key('height') else -1), data['errmsg']]))
	print(count)
	#with open('avplay', 'a') as f:
	#	f.write('\n'.join(lines).encode('utf-8'))
	es.updateStatisticsData('error_avplay', esData)

def readEndTime():
	with open('endTime.ini', 'r') as f:
		return float(f.read())

def writeEndTime(endTime):
	with open('endTime.ini', 'w') as f:
		f.write(str(endTime))
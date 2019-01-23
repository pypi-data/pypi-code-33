#! /usr/bin/env python
# -*- coding: utf-8 -*-

import pyhs2, sys, time, gc
from .. import es

default_encoding = 'utf-8'
if sys.getdefaultencoding() != default_encoding:
	reload(sys)
	sys.setdefaultencoding(default_encoding)

def toHive():
	hiveClient = pyhs2.connect(host='10.168.0.160', port=10000, authMechanism='PLAIN', user='hadoop', password='hadoop', database='default')
	start = int(readEndTime() * 1000)
	while start < (time.time() - 5 * 60) * 1000:
		begin = time.time()
		end = start + 2 * 60 * 1000
		values = []
		for hit in es.scrollSearch('clientlog_read', 'watch', {"size": 10000, "query": {"range": {"create_time": {"gte": start,"lt": end}}}}):
			source = hit['_source']
			body = source['body'].replace('\t', '\\t').replace('\r', '\\r').replace('\n', '\\n').replace("'", "\'")
			values.append("('" + "', '".join([esTimeToHiveTime(source['create_time']), str(source['uid']), esTimeToHiveTime(source['starttime']), esTimeToHiveTime(source['endtime']), body, source['type']]) + "')")
		print(execute(hiveClient, 'insert into log_client partition (date_time="' + timeToPartitionTime(start / 1000) + '") values ' + ','.join(values)))
		writeEndTime(end / 1000)
		print('endTime: ' + str(time.time() - begin) + '(' + es.timeToEsLocalTime(end / 1000) + ')')
		start = end
		time.sleep(2)
		gc.collect()
		break
	close(hiveClient)

def readEndTime():
	with open('endTime.ini', 'r') as f:
		return float(f.read())

def writeEndTime(endTime):
	with open('endTime.ini', 'w') as f:
		f.write(str(endTime))

def execute(hiveClient, sql):
	#print(sql)
	with hiveClient.cursor() as cursor:
		cursor.execute(sql)
		return cursor.fetch()

def close(hiveClient):
	hiveClient.close()

def timeToPartitionTime(pTime):
	return time.strftime('%Y-%m-%d', time.localtime(pTime))

def esTimeToHiveTime(esTime):
	return timeToHiveTime(es.esTimeToTime(esTime))

def timeToHiveTime(pTime):
	return time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(pTime))
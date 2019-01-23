	#! /usr/bin/env python
# -*- coding: utf-8 -*-
import time, sys, MySQLdb, redis
from elasticsearch import Elasticsearch

esTimeFormat = u"%Y-%m-%dT%H:%M:%S.%fZ"
esTimeFormatNoMs = u"%Y-%m-%dT%H:%M:%SZ"

testEsclient = Elasticsearch(['119.23.69.206:9200'], timeout=60)
devEsclient = Elasticsearch(['192.168.0.100:9200'], timeout=60)
localEsclient = Elasticsearch(['127.0.0.1:9200'], http_auth=('elastic', 'changeme'), timeout=60)
dataEsclient = Elasticsearch(['10.168.0.119:9200', '10.168.0.121:9200', '10.168.0.118:9200', '10.168.0.127:9200'], http_auth=('huangzhen', 'df25j0934j4y09hjoijoigef'), timeout=60)
relEsclient = Elasticsearch(['10.32.0.223:9200', '10.33.0.11:9200', '10.167.0.246:9200', '10.0.0.53:9200'], http_auth=('huangzhen', 'huangzhen'), timeout=60)


isTest = True

def setEnv(test):
	global isTest
	isTest = test

def updateRedisWorksHots(worksHots):
	r = redis.Redis(host='r-wz9536616f776d74.redis.rds.aliyuncs.com', port=6379, db=3, password='Idltest503') if isTest else redis.Redis(host='r-bp17063fe90e0e64.redis.rds.aliyuncs.com', port=6379, db=0, password='flrjovlOJEROIJ324')
	
	cacheKeyKey = 'recommend:srv:downgrade:keykey'
	cacheName = 'recommend:srv:downgrade:cache'
	backupCacheName = 'recommend:srv:downgrade:backupcache'

	#print(r.get(cacheKeyKey))
	if r.get(cacheKeyKey) == cacheName:
		r.zadd(backupCacheName, worksHots)
		r.expire(cacheName, 60)
		r.set(cacheKeyKey, backupCacheName)
	else:
		r.zadd(cacheName, worksHots)
		r.expire(backupCacheName, 60)
		r.set(cacheKeyKey, cacheName)

	return True

def searchDbConfig():
	config = {'hotVids': [], 'aidWeights': {}, 'vidWeights': {}}
	
	db = getDb()
	config['hotVids'] = [item[0] for item in searchDb(db, 'select vid from work_whitelist')]
	now = str(int(time.time()))
	for item in searchDb(db, 'select aid, weight from author_weight where start_time <= ' + now + ' and finish_time >= ' + now):
		config['aidWeights'][item[0]] = item[1]
	for item in searchDb(db, 'select vid, weight from work_weight where start_time <= ' + now + ' and finish_time >= ' + now):
		config['vidWeights'][item[0]] = item[1]
	db.close()

	return config

def searchDb(db, sql):
	cursor = db.cursor()
	cursor.execute(sql)
	return cursor.fetchall()

def getDb():
	path = "rm-bp12bzgmvo85rflhio.mysql.rds.aliyuncs.com" if isTest else "rm-bp10b4n5116u90h5t.mysql.rds.aliyuncs.com"
	username = "migration_test" if isTest else "webuser"
	password = "migrationTest*" if isTest else "fnwkufkljfk984ewJ"
	dbName = "idl_night" if isTest else "db_nt_operations"
	return MySQLdb.connect(path, username, password, dbName, charset='utf8')

def updateStatisticsAlias(index, isRead):
	indices = getEsclient().indices
	alias = 'statistics_' + index + '_' + ('read' if isRead else 'write')
	cIndex = indices.get_alias(index=alias).keys()[0]
	newIndex = cIndex[:len(cIndex)-8] if cIndex.endswith('_backups') else cIndex + '_backups'
	body = {
		"actions": [
			{"remove": {"index": cIndex, "alias": alias}},
			{"add": {"index": newIndex, "alias": alias}}
		]
	}
	indices.update_aliases(body=body)

def coverStatisticsData(index, dataDict):
	#先将读别名指向备份，再写入主索引，再将读别名指回
	updateStatisticsAlias(index, True)
	success = coverStatisticsDataReal(index, dataDict)
	#
	time.sleep(20)
	updateStatisticsAlias(index, True)
	if not success:
		return False

	#将写别名指向备份，再写入备份，再将写别名指回
	updateStatisticsAlias(index, False)
	success = coverStatisticsDataReal(index, dataDict)
	updateStatisticsAlias(index, False)
	return success

def coverStatisticsDataReal(index, dataDict):
	fullIndex = 'statistics_' + index + '_write'
	hits = scrollSearch(fullIndex, 'data', {"size": 1}, False)
	updateMark = len(hits) == 0 or not (hits[0]['_source']['updateMark'] if hits[0]['_source'].has_key('updateMark') else False)
	for item in dataDict.values():
		item['updateMark'] = updateMark
	if updateStatisticsData(index, dataDict):
		#操作频繁会发生冲突
		time.sleep(20)
		return deleteStatisticsData(fullIndex, {"query":{"bool":{"must_not":{"term":{"updateMark": updateMark}}}}})
	else:
		return False

def clearStatisticsData(index):
	deleteStatisticsData('statistics_' + index + '_write', {"query":{"match_all":{}}})

def deleteStatisticsData(fullIndex, body, doc_type='data'):
	success = len(getEsclient().delete_by_query(index=fullIndex, doc_type=doc_type, body=body, conflicts='proceed', preference='_primary_first')['failures']) == 0
	getEsclient().delete_by_query(index=fullIndex, doc_type=doc_type, body=body, conflicts='proceed')
	return success

def updateStatisticsData(index, dataDict):
	doc = []
	for key, value in dataDict.items():
		doc.append({"index":{"_id":key}})
		doc.append(value)
	return updateStatisticsDoc(index, doc)

def updateStatisticsDoc(index, doc):
	print('update', index, len(doc) / 2)
	start = 0
	while start < len(doc):
		#sys.stdout.write(str(start) + '\r')
		#sys.stdout.flush()
		end = min(start + 500, len(doc))
		success = updateStatisticsDocResolve(index, doc[start:end])
		if success:
			start = end
	return True

def updateStatisticsDocResolve(index, doc):
	#hot list额外在开发环境存一份用于测试
	#if isTest and index == 'works_hot':
	#	esUpdateStatisticsDocResolve(devEsclient, index, doc)
	success = esUpdateStatisticsDocResolve(getEsclient(), index, doc)
	#正式环境works_actions存一份在本地es用于离线训练
	try:
		if not isTest and index == 'works_actions':
			esUpdateStatisticsDocResolve(localEsclient, index, doc)
	except Exception as error:
		print('save local es error: ' + str(error))

	return success


def esUpdateStatisticsDocResolve(es, index, doc, doc_type='data'):
	return not es.bulk(index='statistics_' + index + '_write', doc_type=doc_type, body=doc)['errors']

def searchStatisticsAggs(index, body):
	fullIndex = 'statistics_' + index + '_read'
	return getEsclient(fullIndex).search(index=fullIndex, doc_type='data', body=body)['aggregations']

def searchPersonas(lastPersonasTime):
	body = {
	  "query":{
	    "bool": {
	      "must": [
	        {
	          "term": {
	            "type": "personas"
	          }
	        },
	        {
	          "range": {
	            "create_time": {
	              "gt": timeToEsTime(lastPersonasTime),
	              "lte": timeToEsTime(min(lastPersonasTime + 12 * 60 * 60, int(time.time()) - 90))
	            }
	          }
	        }
	      ]
	    }
	  },
  		"size": 10000
	}
	return scrollSearch('clientlog_read', 'watch', body)

def searchStatisticsData(index, size=10000, searchAll=True, log=True, version=False):
	return searchStatisticsDataByBody(index, {"size": size}, searchAll, log, version)

def searchStatisticsDataByBody(index, body, searchAll=True, log=True, version=False):
	return scrollSearch('statistics_' + index + '_read', 'data', body, searchAll, log, version)

def scrollSearch(fullIndex, doc_type, body, searchAll=True, log=True, version=False):
	esclient = getEsclient(fullIndex)
	hits = []
	if searchAll:
		result = esclient.search(index=fullIndex, doc_type=doc_type, scroll='1m', body=body, version=version, preference='_primary_first')
		while len(result['hits']['hits']) != 0:
			hits.extend(result['hits']['hits'])
			scroll_id = result['_scroll_id']
			result = esclient.scroll(scroll_id=scroll_id, scroll='1m')
	else:
		hits.extend(esclient.search(index=fullIndex, doc_type=doc_type, body=body, version=version, preference='_primary_first')['hits']['hits'])
	if log:
		print('get', fullIndex, len(hits))
	return hits

def getEsclient(fullIndex=None):
	return testEsclient if isTest else relEsclient if fullIndex == 'works_video_read' else dataEsclient

def timeToEsLocalTime(pTime):
	return time.strftime('%Y-%m-%dT%H:%M:%S+0800', time.localtime(pTime))

def timeToEsTime(pTime, hasMs=False):
	return time.strftime(esTimeFormat if hasMs else esTimeFormatNoMs, time.gmtime(pTime))

def esTimeToTime(esTime, hasMs=False):
	return time.mktime(time.strptime(esTime, esTimeFormat if hasMs else esTimeFormatNoMs)) + 28800



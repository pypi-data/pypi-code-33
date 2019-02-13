"""zk2jy360 - A python upload data API to Jianyan360

	This is a module for the ZhongKong company to upload data to the Jianyan 360 attendance equipment.

Copyright (C) 2019 Jianyan360

This module source should run correctly in CPython versions 2.7 and before version 3.0.
"""
__version__ = '1.0.0'
__token__ = ''
__api__ = 'http://www.jianyan360.com/openapi/zkapi'
version = 'zk2jy360 version ' + __version__

onReq = False
import sys
import os
import json
try:
	import requests
	onReq = True
except ImportError:
	import warnings
	warnings.warn("Python requests package required for zk2jy360.",ImportWarning)

def __sendToJy360(data):
	postdata = {
		'token':__token__
	}
	for record in data:
		for i in data[record]:
			postdata['%s[%d]'%(record,i)] = data[record][i]
	try:
		res = requests.post(url=__api__,data=postdata,timeout=60)
		status_code = res.status_code
		if status_code!=200:
			return {'state':False,'msg':'Server response failed','code':status_code}
		else:
			ret = res.content
			try:
				ret = json.loads(ret)
				if ret['state']==1:
					return {'state':True}
				else:
					return {'state':False,'msg':ret['msg']}
			except Exception, e:
				return {'state':False,'msg':'Server return code exception'}
	except Exception, e:
		return {'state':False,'msg':'Server response failed','code':status_code}

def submit(attnd=None):
	"""
	Upload attendance record
	"""
	if attnd==None or type(attnd)!=list:
		return {'state':False,'msg':'Abnormal attendance records'}

	if len(attnd)<0:
		return {'state':True}

	__data = {
		'realname':{},
		'job_num':{},
		'device_no':{},
		'device_name':{},
		'add_at':{},
		'record_id':{}
	}
	i = 0
	for record in attnd:
		if type(record)!=dict:
			continue
		"""
		Verify data validity
		""" 
		record_keys = record.keys()
		_verify_keys_ = ['ename','pin','alias','sn','checktime','id']
		for _verify_ in _verify_keys_:
			if _verify_ not in record_keys:
				return {'state':False,'msg':'Abnormal attendance records, Not find field `%s`'%(_verify_)}

		"""
		Processing data
		""" 
		__data['realname'][i] = record['ename']
		__data['job_num'][i] = record['pin']
		__data['device_no'][i] = record['sn']
		__data['device_name'][i] = record['alias']
		__data['add_at'][i] = record['checktime']
		__data['record_id'][i] = record['id']
		i += 1

	return __sendToJy360(__data)

if __name__ == "__main__":
	"""
	tester = [
		{
			'ename':'Zhang San',
			'pin':'100001',
			'alias':'XXXX attendance device',
			'sn':'201565894816',
			'checktime':'2019-02-13 08:54:53',
			'id':1
		},
		{
			'ename':'Li si',
			'pin':'100002',
			'alias':'XXXX attendance device',
			'sn':'201565894816',
			'checktime':'2019-02-13 08:55:02',
			'id':2
		}
	]
	__token__ = 'xxxxxxxxxxxxxxxxxxxxxxxxxxxxx'
	result = submit(tester)
	print result
	"""
	pass
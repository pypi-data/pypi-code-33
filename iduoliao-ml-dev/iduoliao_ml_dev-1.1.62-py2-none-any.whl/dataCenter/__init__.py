#! /usr/bin/env python
# -*- coding: utf-8 -*-

import pyhs2

default_encoding = 'utf-8'
if sys.getdefaultencoding() != default_encoding:
	reload(sys)
	sys.setdefaultencoding(default_encoding)

hiveClient = pyhs2.connect(host='10.168.0.160', port=10000, authMechanism='PLAIN', user='hadoop', password='hadoop', database='default')

def query(sql):
	with hiveClient.cursor() as cursor:
		cursor.execute(sql)
		return cursor.fetch()

def close():
	hiveClient.close()
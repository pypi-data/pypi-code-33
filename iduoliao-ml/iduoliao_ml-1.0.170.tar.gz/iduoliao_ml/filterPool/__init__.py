#! /usr/bin/env python
# -*- coding: utf-8 -*-

from btfWorks import BtfWorks

def updateWorks(vids):
	worksList = getWorksList(vids)
	

def getWorksList(vids):
	worksList = {}
	for vid in vids:
		worksList[vid] = BtfWorks(vid)
	syncEsWorks(worksList)
	return worksList

def syncEsWorks(worksList):
	for hit in es.searchStatisticsData('works_filter_pool'):
		vid = hit['_id']
		if worksList.has_key(vid)
			worksList[vid].syncEsData(hit['_source'])

def saveWorksToEs(worksList):
	saveData = {}
	for vid, works in worksList.items():
		saveData[vid] = works.toSaveEsData()
	es.coverStatisticsDataReal('works_filter_pool', saveData)
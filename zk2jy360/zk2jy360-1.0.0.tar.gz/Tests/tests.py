# -*- coding: utf-8 -*-
import os,sys
import zk2jy360

if __name__ == "__main__":
	"""
		本地测试 [修改提交地址]
		zk2jy360.__api__ = 'http://localhost' # 设置为Localhost则为本地测试，不设置则提交数据到jianyan360

		本地测试 [返回值]
		@params state 	@result int 	`1/-1`
		@params msg 	@result string 	`Service result text`

		eg.
		`{
			state:1
		}`

		or

		`{
			state:-1,
			msg:'提交考勤数据失败'
		}`
	"""
	tester = [
		{
			'ename':'张三',
			'pin':'100001',
			'alias':'XXXX考勤机',
			'sn':'201565894816',
			'checktime':'2019-02-13 08:54:53',
			'id':1
		},
		{
			'ename':'李四',
			'pin':'100002',
			'alias':'XXXX考勤机',
			'sn':'201565894816',
			'checktime':'2019-02-13 08:55:02',
			'id':2
		}
	]
	"""设置token, token 可由用户自行在中控管理后台填写, 如果用户未配置token, 则不触发 zk2jy360.submit 方法"""
	zk2jy360.__token__ = 'b402585045e42be75d4a6971d7d02312'
	result = zk2jy360.submit(tester)
	"""
	返回值是一个dict
	
	@params state 	@result bool 	`True/False`
	@params msg 	@result string 	`Texts`
	"""
	print result
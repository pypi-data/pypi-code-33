import logging
import os
import platform


def log_init():
	'''加入run.log，信息打印到屏幕和log文件'''
	logging.basicConfig(level=logging.INFO,
				format='%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s %(message)s',
				datefmt='%a, %d %b %Y %H:%M:%S',
				filename='run.log',
				filemode='w')
	console = logging.StreamHandler()
	console.setLevel(logging.INFO)
	formatter = logging.Formatter('%(name)-12s: %(levelname)-8s %(message)s')
	console.setFormatter(formatter)
	logging.getLogger('').addHandler(console)

	if platform.system() == 'Windows':
		logging.info('执行系统：Windows')
	elif platform.system() == 'Linux':
		logging.info('执行系统：Linux')
	else:
		logging.info('执行系统：Unknown!')


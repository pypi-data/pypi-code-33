from selenium import webdriver
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from datetime import datetime
import platform
import time
from time import sleep
import os
import random
import collections
import logging
import traceback
import csv
import shutil
import pyautogui


class crawler():


	def __init__(self, url="", username="", passwd="", submit="", file_field=""):
		"""初始化，传递网址，账号密码，表头，使用驱动，结果文件，并使用logger日志等"""
		self.url = url
		self.username = username
		self.passwd = passwd
		self.submit = submit
		self.file_field = file_field
		# self.browser = webdriver.Firefox() # firefox打开主页显示不正常，舍弃...
		self.browser = None #webdriver.Chrome()  or webdriver.Firefox() 福建用firefox打开主页显示不正常，而国标委的用firefox更快！要按实际情况选择
		self.total_page = 0 # 目录总页数
		self.xp_nextpage = "" # 下一页的xp
		self.xp_prepage = "" # 上一页的xp
		self.list_total_num = 0 # 每页中的条目数量
		self.list_total_num_last = 0 # 最后一页中的条目数量
		self.counter = 0 # 下一页计数器
		self.csv_file = 'result.csv'
		self.workdir = os.getcwd()
		self.get_dict = collections.defaultdict()
		self.get_list = []
		self.start_page = 1 # 开始爬取的页码，默认从第一页开始爬，也可手动设定，用于断点续爬
		self.start_time = time.perf_counter() # 开始运行时间
		self.running_time = 0 # 已消耗时间，s
		self.total_time = 0 # 估计总共需要消耗时间，s
		self.remained_time = 0 # 估计剩余时间，s


	def exe_loop(self, command, browser, *para, maxcount=3):
		"""循环执行命令command，默认最多循环3次"""
		browser = browser
		if para:
			para = para[0]
			logging.info("Processing: "+command+", "+para)
		else:
			logging.info("Processing: "+command)
		counter = 0
		while True:
			try:
				eval(command)
				logging.info("Exe Success!")
				break
			except:
				logging.info("Exception: "+traceback.format_exc()) # print exception message
				sleep(random.uniform(1, 3))
				if counter >= maxcount:
					break
				else:
					logging.info("waitting for..."+str(counter)+"/"+str(maxcount)+", "+str(int(counter/maxcount*100))+"%")
					counter += 1


	def element_click(self, browser, element_list, sleep_time=5):
		for item in element_list:
			self.exe_loop("WebDriverWait(browser, 1).until(EC.presence_of_element_located((By.XPATH, para))).click()", browser, item)
			sleep(random.uniform(3, sleep_time))


	def get_reset(self):
		"""清空数据获取字典和列表"""
		self.get_dict = collections.defaultdict()
		self.get_list = []


	def get_runningtime(self, process):
		"""查看完成进度，消耗时间，总消耗时间和剩余时间，打印到log"""
		self.running_time = (time.perf_counter() - self.start_time) # 已消耗时间，s
		self.total_time = self.running_time/process # 估计总共需要消耗时间，s
		self.remained_time = self.total_time - self.running_time # 估计剩余时间，s

		logging.info("完成进度: "+str(round(process*100, 2))+"%")
		logging.info("已消耗时间: "+str(round(self.running_time, 2))+"s，"+str(round(self.running_time/3600, 2))+"h")
		logging.info("估计剩余时间: "+str(round(self.remained_time, 2))+"s，"+str(round(self.remained_time/3600, 2))+"h")
		logging.info("估计总共需要消耗时间: "+str(round(self.total_time, 2))+"s，"+str(round(self.total_time/3600, 2))+"h")


	def login(self):
		"""登录主页"""
		self.exe_loop("browser.get(para)", self.browser, self.url)
		self.browser.maximize_window()
		sleep(random.uniform(1, 3))


	def refresh_check(self, fun_try, fun_except, current_item, maxcount=3, maxrefresh=3):
		'''首先判断该记录的获取页面是否成功，如果成功则跳出循环，否则等待，等待次数大于maxcount时，会刷新页面。当刷新次数大于maxrefre时，会跳出while循环，继续后续程序'''
		counter = 0
		counter_refresh = 0
		
		while True:
			try:
				get_fun_try = fun_try()
				if get_fun_try == 'Exception':
					raise Exception
				logging.info("当前记录获取成功："+str(current_item)) # current_item是当前记录，必须为str
				sleep(random.uniform(1, 3))
				break # 成功获取则退出
			except:
				sleep(random.uniform(1, 3))
				logging.info("当前记录获取失败！将自动重新获取："+str(current_item))
				logging.info("Exception: "+traceback.format_exc()) # print exception message
				if counter >= maxcount: # 如果失败并且大于获取次数时，刷新
					counter = 0
					try:
						pyautogui.press('f5') #	self.browser.refresh()会卡浏览器!
						sleep(random.uniform(1, 3))
					except:
						logging.info("Exception: "+traceback.format_exc()) # print exception message
						pass	
					sleep(random.uniform(1, 3))
					fun_except()
					counter_refresh += 1
					if counter_refresh >= maxrefresh: # 如果大于刷新次数的话，会返回一个字符串并跳出循环
						return 'continue'
						break # 获取不成功但超过最大刷新次数获取也退出
				else:
					logging.info("waitting for..."+str(counter)+"/"+str(maxcount)+", "+str(int(counter/maxcount*100))+"%")
					counter += 1
					sleep(random.uniform(1, 3))


	def csv_export(self, data):
		"""创建并写入结果result.csv文件，首先判读result.csv是否存在，不存在则创建并写入表头，存在则增量写入文件。注意，不同操作系统的encoding是不同的。data格式：[{}]， self.file_field格式:['','']"""
		# 如果'result.csv'不存在，则创建文件，写入表头
		if not(os.path.exists(self.csv_file)):	
			logging.info('创建result.csv文件')
			# with open(csvfile_name, 'a', encoding='GBK', newline='') as csvfile: #FineBI
			if platform.system() == 'Windows':
				csvfile = open(self.csv_file, 'w', encoding='UTF8', newline='')
			elif platform.system() == 'Linux':
				csvfile = open(self.csv_file, 'w', newline='')
			writer = csv.DictWriter(csvfile, fieldnames=self.file_field)
			writer.writeheader()
			csvfile.close()
		
		# 如果'result.csv'存在，则增量写入文件
		logging.info('写入result.csv文件')
		if platform.system() == 'Windows':
			csvfile = open(self.csv_file, 'a', encoding='UTF8', newline='')
		elif platform.system() == 'Linux':
			csvfile = open(self.csv_file, 'a', newline='')
		writer = csv.DictWriter(csvfile, fieldnames=self.file_field)
		writer.writerows(data)
		csvfile.close()


	def done(self):
		"""成功完成后，copy文件，打印完成信息"""
		timenow = datetime.strptime(str(datetime.now().year)+"_"+str(datetime.now().month)+"_"+str(datetime.now().day)+"_"+str(datetime.now().hour)+":"+str(datetime.now().minute)+":"+str(datetime.now().second), "%Y_%m_%d_%H:%M:%S")

		try:
			os.mkdir("result")
		except:
			shutil.copyfile("result.csv", self.workdir+"/result/result_"+str(timenow).replace(' ', '_').replace(':', '_')+".csv")

		logging.info('------------------------------------------------------')
		logging.info('运行完毕，请检查并备份result.csv文件！')


	def page_list_num(self):
		"""调整每页条目数量"""
		pass


	def get_xp_std(self, index):
		"""获取标准表头的xpath"""
		pass


	def get_data(self):
		"""爬取模板"""
		pass


from selenium import webdriver
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
import smtplib    
from email.mime.multipart import MIMEMultipart    
from email.mime.text import MIMEText    
from email.mime.image import MIMEImage 
from email.header import Header   
from datetime import datetime
import platform
from time import sleep
import os
import logging
import traceback


class autoom():


	def __init__(self, crontab_time, delay_start=False):

		self.workdir 			= os.getcwd()
		self.crontab_time 		= crontab_time # everyday exec time
		self.delay_start 		= delay_start # False means start process this time, True means next time
		self.receivers 			= [] #['xx@xxx.com']
		self.smtpserver 		= '' #'smtp.exmail.qq.com'
		self.mail_username 		= ''# 'xx@xxx.com'
		self.mail_password		= ''# sender email password
		self.mail_sender		= ''# sender email 'xx@xx.com'
		self.reportfile         = "%s"%(self.workdir)+"report.txt" # report.txt

	def sleep_second(self, crontab_time, now):
		'''crontab sleep time'''
		if (crontab_time-now).total_seconds() >= 0:
			return float((crontab_time-now).total_seconds())
		elif (crontab_time-now).total_seconds() < 0:
			return float(86400.00+(crontab_time-now).total_seconds())


	def mail(self, receiver):
		'''auto send email to receiver'''

		smtpserver = self.smtpserver
		msg = MIMEMultipart('mixed') 
		msg['Subject'] = self.subject
		msg['From'] = self.mail_sender
		msg['To'] = receiver
		with open(self.reportfile, 'r') as f:	# with open(reportfile, 'r', encoding='utf-8') / with open(reportfile, 'r', encoding='gbk')
			text = f.read()
		text_plain = MIMEText(text,'plain', 'utf-8')
		msg.attach(text_plain)    
		# smtp = smtplib.SMTP()
		smtp = smtplib.SMTP_SSL()
		smtp.connect('smtp.exmail.qq.com')
		smtp.login(self.mail_username, self.mail_password)    
		smtp.sendmail(self.mail_sender, receiver, msg.as_string())    
		smtp.quit()	


	def mail_content(receiver, shopind):
		pass


	def pycrontab(self):
		switch = "on"
		while True:
			now = datetime.strptime(str(datetime.now().year)+"-"+str(datetime.now().month)+"-"+str(datetime.now().day)+" "+str(datetime.now().hour)+":"+str(datetime.now().minute)+":"+str(datetime.now().second), "%Y-%m-%d %H:%M:%S")
			crontab_time = datetime.strptime(str(datetime.now().year)+"-"+str(datetime.now().month)+"-"+str(datetime.now().day)+" "+self.crontab_time, "%Y-%m-%d %H:%M:%S")
			if (now >= crontab_time) and (switch == "on"):
				switch = "off"
				try:
					with open(self.reportfile, 'w') as f:
						now = datetime.strptime(str(datetime.now().year)+"-"+str(datetime.now().month)+"-"+str(datetime.now().day)+" "+str(datetime.now().hour)+":"+str(datetime.now().minute)+":"+str(datetime.now().second), "%Y-%m-%d %H:%M:%S")
						f.write( "执行系统: "+str(platform.platform()))
						f.write("\n")
						f.write( "报告时间: "+str(now))
						f.write("\n")
						f.write("\n")
						
					self.main()

				except:
					logging.info("Exception: "+traceback.format_exc()) # print exception message
					with open(self.reportfile, 'a') as f:
						f.write("执行错误, 请检查!")
						f.write("Exception: "+traceback.format_exc())
						f.write('\n')
						f.write('\n')	

				finally:
					for receiver in self.receivers:
						self.mail(receiver)
			else:
				switch = "on"
				print(now)
				print("Waitting for the right time to start,%s s left..."%(str(self.sleep_second(crontab_time, now))))
				sleep(self.sleep_second(crontab_time, now)+10)


	def main(self):
		pass


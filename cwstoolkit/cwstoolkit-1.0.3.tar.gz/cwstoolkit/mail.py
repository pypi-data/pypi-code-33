#!/usr/bin/env python
# encoding: utf-8
# Author: colinspace
# Date: 2018
# Desc:
#

import os
import sys

if sys.version_info.major == 2:
    import ConfigParser as configparser
elif sys.version_info.major == 3:
    import configparser


import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.image import MIMEImage


from cwstoolkit import settings

class Mail():
	"""
	mail class
	"""

	def __init__(self, configfile=None, section='mail', subject='Test Email by Python', userlist=None, content=None, ctype='text', attachment=None, atype='file'):
		self.configfile = configfile
		self.section = section
		self.subject = subject
		self.userlist = userlist
		self.content = content
		self.ctype = ctype
		self.attachment = attachment
		self.atype = atype

	def getConfig(self):
		mailconfig = {}
		config = configparser.ConfigParser()
		config.read(self.configfile)
		mailconfig['host'] = config.get(self.section, 'HOST')
		mailconfig['user'] = config.get(self.section, 'USER')
		mailconfig['password'] = config.get(self.section, 'PASSWORD')
		mailconfig['port'] = config.get(self.section, 'PORT')

		return mailconfig

	def send(self):
		ret = {}
		mailconfig = self.getConfig()
		to_addrs = self.userlist.split(',')
		basename = ''

		msg = MIMEMultipart()
		msg['From'] = mailconfig['user']
		msg['Subject'] = self.subject
		msg['To']  = ','.join(to_addrs)


		if self.ctype == 'text':
			msg.attach(MIMEText(self.content, 'plain', 'utf-8'))
		elif self.ctype == 'html':
			msg.attach(MIMEText(self.content, 'html', 'utf-8'))

		## 多个附件，而且是不同类型的文件
		if self.attachment:
			for item in self.attachment.split(','):
				basename = os.path.basename(item)
				ext = os.path.basename(item).split('.')[-1]
				lower_ext = ext.lower()
				if lower_ext in settings.file_ext_list or lower_ext in settings.archive_ext_list:
					with open(item, 'r') as f:
						content_file = f.read()
						attach_file = MIMEText(content_file, 'plain', 'utf-8')
						attach_file['Content-Type'] = 'application/octet-stream'
						attach_file['Content-Disposition'] = 'attachment;filename=%s' % basename
						msg.attach(attach_file)
				elif lower_ext in settings.image_ext_list:
					with open(item, 'rb') as f:
                        			attach_image = MIMEImage(f.read())
						attach_image['Content-Type'] = 'application/octet-stream'
						attach_image['Content-Disposition'] = 'attachment;filename="1.png"'
						msg.attach(attach_image)
				
		try:
			server = smtplib.SMTP_SSL()
			server.connect(mailconfig['host'])
			server.login(mailconfig['user'], mailconfig['password'])
			server.sendmail(mailconfig['user'], to_addrs, msg.as_string())
			ret['code'] = 200, 
			ret['msg'] = 'send mail success !'
			# server.quit()
		except Exception as e:
			# senderr = str(e)
			ret['code'] = 5005
			ret['msg'] = 'send mail failed! exception like: %s' % str(e)	

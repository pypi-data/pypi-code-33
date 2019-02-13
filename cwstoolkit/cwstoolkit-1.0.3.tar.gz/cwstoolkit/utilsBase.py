#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author: Colin
# Date: 2017-05-11
# Desc: 自定义基础函数
#


import os

import sys
import hashlib 
import string
from random import choice

import socket
import fcntl
import struct
import commands

COLORS = {
	"reset": "\033[0m",
	"black": "\033[1;30m",
	'red': '\033[1;31m',
	'green': '\033[1;32m',
	'yellow': '\033[1;33m',
	'blue': '\033[1;34m',
	'magenta': '\033[1;35m',
	'cyan': '\033[1;36m',
	'white': '\033[1;37m',
	'bgred': '\033[1;41m',
	'bggrey': '\033[1;100m'
}


def colorMsg(color, msg):
	"""
	return msg with given color
	param color:
		black
		red
		green
		yellow
		blue
		magenta
		cyan
		white
		bgred
		bggrey

	print(colorMsg("blue", "hello world")) 
	"""
	return COLORS[color] + msg + COLORS['reset']


def getMD5(object):
	"""
	return hash value from file, string or folder
	"""
	md5_hash = None
	if os.path.isfile(object):
		with open(object, 'rb') as fd:
			md5_hash = hashlib.md5(fd.read()).hexdigest()
	elif os.path.isdir(object):
		md5_hash = hashlib.md5()
		for root, dirs, files in os.walk(object):
			#dirs[:] = sorted(dirs)
			for f in sorted(files):
				with open(os.path.join(root, f), 'rb') as fd:
					md5_hash.update(fd.read())
		md5_hash = md5_hash.hexdigest()
	elif isinstance(object, str):
		md5_hash = hashlib.md5(object).hexdigest()
	else:
		print(colorMsg('red', 'get MD5 for file or directory and please give right param'))

	return md5_hash

def generate_passwd(passwd_length=16):
	"""
	function to generate a password
	return passwd
	"""
	passwd = []
	# passwd_length = 16
	passwd_seed = string.digits + string.ascii_letters + '!@#$%^&'

	while(len(passwd) < passwd_length):
		passwd.append(choice(passwd_seed))

	return ''.join(passwd)


def getIPAdress(ifname='eth0'):
	'''
	利用Python socket模块 得到给定网口对应的当前主机的IP地址
	'''
	s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
	
	return socket.inet_ntoa(fcntl.ioctl(
			s.fileno(),
			0x8915,  # SIOCGIFADDR
			struct.pack('256s', ifname[:15]))[20:24])

def getIPAdress2():
	'''
	利用Linux命令`ip` 得到当前主机的IP
	'''
	_, ip = commands.getstatusoutput("""echo `/sbin/ip a | grep -E "eth[0-9]$|em[0-9]$|br[0-9]$|bond[0-9]$"|grep -E '[0-9]{1,3}/[0-9]{1,2}'| awk '{print $2}'|awk -F "/" '{print $1}'  | awk -F '.' '{print $0}'`""")
	return ip

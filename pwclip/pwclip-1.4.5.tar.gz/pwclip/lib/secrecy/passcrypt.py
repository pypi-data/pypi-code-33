#!/usr/bin/env python3
# -*- encoding: utf-8 -*-
"""passcrypt module"""

from os import path, remove, environ, chmod, stat, makedirs

import socket

from time import time

from yaml import load, dump

from paramiko.ssh_exception import SSHException

from colortext import bgre, tabd, error

from system import userfind, filerotate, setfiletime

from net.ssh import SecureSHell

from secrecy.gpgtools import GPGTool, GPGSMTool

class PassCrypt(object):
	"""passcrypt main class"""
	dbg = None
	aal = None
	fsy = None
	sho = None
	gsm = None
	gui = None
	try:
		user = userfind()
		home = userfind(user, 'home')
	except FileNotFoundError:
		user = environ['USERNAME']
		home = path.join(environ['HOMEDRIVE'], environ['HOMEPATH'])
	user = user if user else 'root'
	home = home if home else '/root'
	plain = path.join(home, '.pwd.yaml')
	crypt = path.join(home, '.passcrypt')
	remote = ''
	reuser = user
	recvs = []
	if 'GPGKEYS' in environ.keys():
		recvs = environ['GPGKEYS'].split(' ')
	elif 'GPGKEY' in environ.keys():
		recvs = [environ['GPGKEY']]
	sslcrt = ''
	sslkey = ''
	__weaks = {}
	__oldweaks = {}
	def __init__(self, *args, **kwargs):
		"""passcrypt init function"""
		for arg in args:
			if hasattr(self, arg):
				setattr(self, arg, True)
		for (key, val) in kwargs.items():
			if hasattr(self, key):
				setattr(self, key, val)
		if self.dbg:
			print(bgre(PassCrypt.__mro__))
			print(bgre(tabd(PassCrypt.__dict__, 2)))
			print(' ', bgre(self.__init__))
			print(bgre(tabd(self.__dict__, 4)))
		self.cryptrecvs = GPGTool().recvlist(self.crypt)
		now = int(time())
		cache = '%s/.cache'%self.home
		timefile = '%s/pwclip.time'%cache
		if not path.exists(cache):
			makedirs(cache)
		age = None
		if not path.exists(timefile):
			with open(timefile, 'w+') as tfh:
				tfh.write(str(now))
			age = 14401
		self.age = int(now-int(stat(timefile).st_mtime)) if not age else age
		gsks = GPGSMTool().keylist(True)
		if self.gsm or (
              self.gsm is None and self.recvs and [
                  r for r in self.recvs if r in gsks]):
			self.gpg = GPGSMTool(*args, **kwargs)
		else:
			self.gpg = GPGTool(*args, **kwargs)
		self.ssh = SecureSHell(*args, **kwargs)
		write = False
		if self.remote and self._copynews_():
			write = True
		__weaks = self._readcrypt()
		self.__oldweaks = __weaks
		try:
			with open(self.plain, 'r') as pfh:
				__newweaks = load(pfh.read())
			if not self.dbg:
				remove(self.plain)
			write = True
		except FileNotFoundError:
			__newweaks = {}
		if __newweaks:
			__weaks = __weaks if __weaks else {}
			for (su, ups) in __newweaks.items():
				for (usr, pwdcom) in ups.items():
					if su not in __weaks.keys():
						__weaks[su] = {}
					__weaks[su][usr] = pwdcom
		self.__weaks = __weaks
		if write:
			self._writecrypt(__weaks)

	def _copynews_(self):
		"""copy new file method"""
		if self.dbg:
			print(bgre(self._copynews_))
		if int(self.age) > 14400 and self.remote:
			try:
				return self.ssh.scpcompstats(
                    self.crypt, path.basename(self.crypt),
                    remote=self.remote, reuser=self.reuser)
			except (FileNotFoundError, socket.gaierror):
				pass
			except SSHException as err:
				error(err)
		return False

	def _chkcrypt(self, __weak):
		"""crypt file checker method"""
		if self.dbg:
			print(bgre(self._chkcrypt))
		if self._readcrypt() == __weak:
			return True
		return False

	def _readcrypt(self):
		"""read crypt file method"""
		if self.dbg:
			print(bgre(self._readcrypt))
		try:
			with open(self.crypt, 'r') as vlt:
				crypt = vlt.read()
		except FileNotFoundError:
			return False
		return load(str(self.gpg.decrypt(crypt)))

	def _writecrypt(self, __weak, force=None):
		"""crypt file writing method"""
		if self.dbg:
			print(bgre(self._writecrypt))
		kwargs = {'output': self.crypt}
		filerotate(self.crypt, 2)
		now = None
		for _ in range(0, 2):
			isok = self.gpg.encrypt(message=dump(__weak), **kwargs)
			if self._chkcrypt(__weak):
				chmod(self.crypt, 0o600)
				now = int(time())
				setfiletime(self.crypt, (now, now))
				if self.remote:
					self._copynews_()
		if now is None:
			self.gpg.encrypt(message=dump(self.__oldweaks), **kwargs)
		return True

	def adpw(self, usr, pwd=None, com=None):
		"""password adding method"""
		if self.dbg:
			print(bgre(tabd({
                self.adpw: {'user': self.user, 'entry': usr,
                            'pwd': pwd, 'comment': com}})))
		pwdcom = [pwd if pwd else self.gpg.passwd()]
		if not pwd and not com:
			com = input('enter a comment: ')
		if com:
			pwdcom.append(com)
		if self.dbg:
			print('%s\n adduser = %s addpass = %s'%(
                self.adpw, usr, pwd))
		__weak = self._readcrypt()
		if not self.aal:
			if not self.user in __weak.keys():
				__weak[self.user] = {}
			__weak[self.user][usr] = pwdcom
		else:
			for u in __weak.keys():
				__weak[u][usr] = pwdcom
		self._writecrypt(__weak)
		return __weak

	def chpw(self, usr, pwd=None, com=None):
		"""change existing password method"""
		if self.dbg:
			print(bgre(tabd({
                self.chpw: {'user': self.user, 'entry': usr, 'pwd': pwd}})))
		pwdcom = [pwd if pwd else self.gpg.passwd()]
		if not pwd and not com:
			com = input('enter a comment: ')
		if com:
			pwdcom.append(com)
		__weak = self._readcrypt()
		if __weak and self.user in __weak.keys() and \
              usr in __weak[self.user].keys():
			__weak[self.user][usr] = pwdcom
			self._writecrypt(__weak)
		return __weak

	def rmpw(self, usr):
		"""remove password method"""
		if self.dbg:
			print(bgre(tabd({self.rmpw: {'user': self.user, 'entry': usr}})))
		__weak = self._readcrypt()
		if self.aal:
			for u in __weak.keys():
				try:
					del __weak[u][usr]
				except KeyError:
					error('entry', usr, 'could not be found for', u)
		else:
			try:
				del __weak[self.user][usr]
			except KeyError:
				error('entry', usr, 'could not be found for', self.user)
		if self._writecrypt(__weak):
			if self.remote:
				self._copynews_()
		return __weak

	def lspw(self, usr=None, aal=None):
		"""password listing method"""
		if self.dbg:
			print(bgre(tabd({self.lspw: {'user': self.user, 'entry': usr}})))
		aal = True if aal else self.aal
		__ents = {}
		if self.__weaks:
			if aal:
				__ents = self.__weaks
				if usr:
					usrs = [self.user] + \
                        [u for u in self.__weaks.keys() if u != self.user]
					for user in usrs:
						if user in self.__weaks.keys() and \
                              usr in self.__weaks[user].keys():
							__ents = {usr: self.__weaks[user][usr]}
							break
			elif self.user in self.__weaks.keys():
				__ents = self.__weaks[self.user]
				if usr in __ents.keys():
					__ents = {usr: self.__weaks[self.user][usr]}
		if self.recvs != self.cryptrecvs:
			error('recipients for encryption have changed from:\n  ',
                ' '.join(self.cryptrecvs), '\nto:\n  ',
                ' '.join(self.recvs), '\nreencryption is enforced')
			self._writecrypt(self.__weaks, force=True)
		return __ents

def lscrypt(usr, dbg=None):
	"""passlist wrapper function"""
	if dbg:
		print(bgre(lscrypt))
	__ents = {}
	if usr:
		__ents = PassCrypt().lspw(usr)
	return __ents




if __name__ == '__main__':
	exit(1)

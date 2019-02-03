#!/usr/bin/env python3
# -*- encoding: utf-8 -*-
"""
gpgtool module
"""
from os import path, environ, remove, name as osname
try:
	from os import uname
except ImportError:
	def uname(): return [0][environ['COMPUTERNAME']]

from getpass import getpass

from tkinter import TclError

from gnupg import GPG

import wget

#try:
#	import readline
#except ImportError:
#	pass

# local imports
from colortext import blu, yel, bgre, tabd, abort, error, fatal

from system import xyesno, xgetpass, xmsgok, xinput, userfind, which

from executor import command as cmd

class GPGTool(object):
	"""
	gnupg wrapper-wrapper :P
	although the gnupg module is quite handy and the functions are pretty and
	useable i need some modificated easing functions to be able to make the
	main code more easy to understand by wrapping multiple gnupg functions to
	one - also i can prepare some program related stuff in here
	"""
	dbg = None
	gui = None
	iac = None
	__c = 0
	__ppw = None
	homedir = path.join(path.expanduser('~'), '.gnupg')
	if 'GNUPGHOME' in environ.keys():
		homedir = environ['GNUPGHOME'].strip()
	__bin = 'gpg2'
	if osname == 'nt':
		homedir = path.join(
            path.expanduser('~'), 'AppData', 'Roaming', 'gnupg')
		__bin = 'gpg.exe'
	_binary = which(__bin)
	_keyserver = ''
	kginput = {}
	recvs = []
	if 'GPGKEYS' in environ.keys():
		recvs = environ['GPGKEYS'].split(' ')
	elif 'GPGKEY' in environ.keys():
		recvs = [environ['GPGKEY']]
	def __init__(self, *args, **kwargs):
		"""gpgtool init function"""
		for arg in args:
			if hasattr(self, arg):
				setattr(self, arg, True)
		for (key, val) in kwargs.items():
			if hasattr(self, key):
				setattr(self, key, val)
		if osname == 'nt' and not which('gpg.exe'):
			if not xyesno('mandatory gpg4win not found! Install it?'):
				exit(1)
			import wget
			src = 'https://files.gpg4win.org/gpg4win-latest.exe'
			trg = path.join(environ['TEMP'], 'gpg4win.exe')
			wget.download(src, out=trg)
			cmd.call(trg)
			remove(trg)
		if self.dbg:
			print(bgre(GPGTool.__mro__))
			print(bgre(tabd(GPGTool.__dict__, 2)))
			print(' ', bgre(self.__init__))
			print(bgre(tabd(self.__dict__, 4)))

	@property                # keyring <str>
	def keyring(self):
		"""pubring getter (read-only)"""
		if self.binary.endswith('.exe'):
			return path.join(self.homedir, 'pubring.gpg')
		return path.join(self.homedir, 'pubring.kbx') \
			if self.binary.endswith('2') else path.join(
                self.homedir, 'pubring.gpg')

	@property                # secring <str>
	def secring(self):
		"""secring getter (read-only)"""
		if self.binary.endswith('.exe'):
			return path.join(self.homedir, 'secring.gpg')
		elif self.binary.endswith('2') and self.keyring.endswith('gpg'):
			return path.join(self.homedir, 'secring.gpg')
		return path.join(self.homedir, 'secring.kbx')

	@property                # binary <str>
	def binary(self):
		"""binary path getter"""
		return self._binary
	@binary.setter
	def binary(self, val):
		"""binary path setter"""
		self._binary = val

	@property                # _gpg_ <GPG>
	def _gpg_(self):
		"""gpg wrapper property"""
		opts = ['--batch', '--always-trust']
		if osname != 'nt' and self.binary.rstrip('.exe').endswith('2'):
			opts.append('--pinentry-mode=loopback')
		elif self.__c >= 1:
			opts.append('--passphrase="%s"'%self.__ppw)
		__g = GPG(
            keyring=self.keyring, secret_keyring=self.secring,
            gnupghome=self.homedir, gpgbinary=self.binary,
            use_agent=True, options=opts,
            verbose=1 if self.dbg else 0)
		if osname != 'nt':
			__g.encoding = 'utf-8'
		return __g

	@staticmethod
	def passwd(rpt=False, gui=None):
		"""password questioning method"""
		pas = getpass
		err = error
		if gui:
			pas = xgetpass
			err = xmsgok
		msg = 'enter passphrase: '
		tru = 'repeat that passphrase: '
		while True:
			if not rpt:
				return pas(msg)
			__pwd = pas(msg)
			if __pwd == pas(tru):
				return __pwd
			err('passwords did not match')
		return False

	@staticmethod
	def __find(pattern, *vals):
		"""pattern matching method"""
		for val in vals:
			if isinstance(val, (list, tuple)) and \
                  [v for v in val if pattern in v]:
				return True
			elif pattern in val:
				return True
		return False

	@staticmethod
	def __gendefs(gui=False):
		user = environ['USERNAME'] if osname == 'nt' else environ['USER']
		host = environ['COMPUTERNAME'] if osname == 'nt' else uname()[1]
		kginput = {
                'name_real': user,
                'name_comment': '',
                'name_email': '%s@%s'%(user, host),
                'expire_date': 0,
                'key_type': 'RSA',
                'key_length': 4096,
                'subkey_type': 'RSA',
                'subkey_length': 4096}
		bea = False
		while True:
			echo = print
			ynq = ask = input
			msg = '%s\n%s\nIs that OK? [Y/n]\n'%(
				blu('generating keys using:'), yel(tabd(kginput, 2)))
			if gui:
				echo = xmsgok
				ynq = xyesno
				ask = xinput
				msg = 'generating keys using:\n%s\n\nIs that OK? [Y/n]\n'%tabd(
					   kginput, 2)
			try:
				yna = ynq(msg)
			except TclError as err:
				print(err)
				break
			if yna in ('n', False, None):
				while True:					
					for (k, v) in kginput.items():
						cva = ynq(
							'change value for "%s", currently is "%s"? [Y/n]'%(
								k, v))
						if cva is True or cva in ('y', ''):
							__nv = ask(
								'enter new value for %s (is %s)'%(k, v))
							kginput[k] = __nv
					bea = ynq('generating keys using:\n%s\n\nIs that OK? ' \
					    	  '[Y/n]\n'%tabd(kginput))
					if bea is True or bea in ('n', ''):
						break
			elif yna in ('y', '', True):
				break
			if bea is not False:
				break
		return kginput

	def recvlist(self, crypt):
		keys = []
		if path.isfile(crypt):
			with open(crypt, 'r') as cfh:
				crypt = cfh.read()
		_, recvs = cmd.stdx('gpg --list-only -v -d', inputs=crypt)
		if recvs:
			for k in recvs.split('\n'):
				if k.startswith('gpg: public key is'):
					keys.append('0x%s'%(str(list(self.findkey(
                        k.split(' ')[-1]).keys())[0])[-16:]))
		return keys

	def genkeys(self, **kginput):
		"""key-pair generator method"""
		if self.dbg:
			print(bgre(self.genkeys))
		kginput = kginput if kginput else self.__gendefs(self.gui)
		if 'passphrase' not in kginput.keys():
			kginput['passphrase'] = self.passwd(True, self.gui)
		self._gpg_.gen_key(self._gpg_.gen_key_input(**kginput))
		return list(self.findkey().keys())[0]

	def findkey(self, pattern='', **kwargs):
		"""key finder method"""
		typ = 'A' if 'typ' not in kwargs.keys() else kwargs['typ']
		sec = False if 'secret' not in kwargs.keys() else kwargs['secret']
		keys = {}
		pattern = pattern if not pattern.startswith('0x') else pattern[2:]
		for key in self._gpg_.list_keys(secret=sec):
			if pattern and not self.__find(pattern, *key.values()):
				continue
			subs = {}
			for (k, _) in key.items():
				if k == 'subkeys':
					#print(k)
					for sub in key[k]:
						#print(sub)
						_, typs, finger = sub
						#print(finger, typs)
						if typ == 'A' or (typ in typs):
							subs[finger] = typs
			keys[key['fingerprint']] = subs
		return keys

	def keyimport(self, key):
		"""key from string import method"""
		if self.dbg:
			print(bgre('%s %s'%(self.keyimport, key)))
		return self._gpg_.import_keys(key)

	def keyexport(self, *patterns, **kwargs):
		"""key to string export method"""
		if self.dbg:
			print(bgre('%s %s'%(self.keyexport, patterns)))
		keys = dict((k, v) for (k, v) in self.findkey(**kwargs).items())
		if patterns:
			keys = dict((k, v) for p in list(patterns) \
                for (k, v) in self.findkey(p, **kwargs).items())
		return keys

	def _encryptwithkeystr(self, message, keystr, output):
		"""encrypt using given keystring method"""
		fingers = [
            r['fingerprint'] for r in self._gpg_.import_keys(keystr).results]
		return self._gpg_.encrypt(
            message, fingers, output=output)

	def encrypt(self, message, **kwargs):
		"""text encrypting method"""
		if self.dbg:
			print(bgre(self.encrypt))
		recvs = list(self.keyexport())
		if 'GPGKEYS' in environ.keys():
			recvs = [k for k in environ['GPGKEYS'].split(' ') if k]
		elif 'GPGKEY' in environ.keys():
			recvs = [environ['GPGKEY']] + [
                k for k in recvs if k != environ['GPGKEY']]
		if not recvs:
			recvs = self.genkeys()
		fingers = list(self.keyexport(*recvs, **{'typ': 'e'}))
		out = None if 'output' not in kwargs.keys() else kwargs['output']
		self._gpg_.encrypt(
            message, fingers, always_trust=True, output=out)

	def decrypt(self, message, output=None):
		"""text decrypting method"""
		if self.dbg:
			print(bgre(self.decrypt))
		while self.__c < 5:
			__plain = self._gpg_.decrypt(
                message.strip(), always_trust=True,
                output=output, passphrase=self.__ppw)
			if __plain.ok:
				return __plain
			yesno = True
			if self.__c > 3:
				yesno = False
				try:
					xmsgok('too many wrong attempts')
				except TclError:
					fatal('too many wrong attempts')
				exit(1)
			elif self.__c >= 1 and self.__c < 3:
				yesno = False
				try:
					yesno = xyesno('decryption failed - try again?')
				except TclError:
					yesno = True if str(input(
                        'decryption failed - retry? [Y/n]'
                        )).lower() in ('y', '') else False
			if not yesno:
				raise PermissionError('%s cannot decrypt'%self.decrypt)
			self.__c += 1
			try:
				self.__ppw = self.passwd()
			except KeyboardInterrupt:
				return False
		return False


class GPGSMTool(GPGTool):
	"""GPGSMTool class for compatibility to SSL keys/certificates"""
	dbg = False
	homedir = path.join(path.expanduser('~'), '.gnupg')
	__gsm = 'gpgsm'
	__ssl = 'openssl'
	if osname == 'nt':
		homedir = path.join(
            path.expanduser('~'), 'AppData', 'Roaming', 'gnupg')
		__gsm = 'gpgsm.exe'
		__ssl = 'openssl.exe'
	_gsmbin = which(__gsm)
	_sslbin = which(__ssl)
	sslcrt = ''
	sslkey = ''
	sslca = ''
	recvs = []
	def __init__(self, *args, **kwargs):
		for arg in args:
			if hasattr(self, arg):
				setattr(self, arg, True)
		for (key, val) in kwargs.items():
			if hasattr(self, key):
				setattr(self, key, val)
		if not self.recvs:
			if 'GPGKEYS' in environ.keys():
				self.recvs = environ['GPGKEYS'].split(' ')
			elif 'GPGKEY' in environ.keys():
				self.recvs = [environ['GPGKEY']]
		if self.sslcrt and self.sslkey:
			if osname == 'nt':
				raise RuntimeError(
                    'ssl import is currently not available for windows')
			self.sslimport(self.sslkey, self.sslcrt, self.sslca)
		if self.dbg:
			print(bgre(GPGSMTool.__mro__))
			print(bgre(tabd(GPGSMTool.__dict__, 2)))
			print(' ', bgre(self.__init__))
			print(bgre(tabd(self.__dict__, 4)))
		GPGTool.__init__(self, *args, **kwargs)

	def sslimport(self, key, crt, ca):
		"""ssl key/cert importing method"""
		if self.dbg:
			print(bgre('%s key=%s crt=%s'%(self.sslimport, key, crt)))
		cmd.stdo('%s --import'%self._gsmbin, inputs=cmd.stdo(
            '%s pkcs12 -export -chain -CAfile %s -in %s -inkey %s'%(
                self._sslbin, ca, crt, key), b2s=False), b2s=False)

	def keylist(self, secret=False):
		"""key listing function"""
		if self.dbg:
			print(bgre(self.keylist))
		gsc = 'gpgsm -k'
		if secret:
			gsc = 'gpgsm -K'
		kstrs = cmd.stdo(gsc)
		keys = []
		if kstrs:
			kstrs = str('\n'.join(kstrs.split('\n')[2:])).split('\n\n')
			for ks in kstrs:
				if not ks: continue
				kid = str(ks.split('\n')[0].strip()).split(': ')[1]
				inf = [i.strip() for i in ks.split('\n')[1:]]
				key = {kid: {}}
				for i in inf:
					key[kid][i.split(': ')[0]] = i.split(': ')[1]
				keys.append(key)
		return keys

	def encrypt(self, message, **kwargs):
		"""text encrypting method"""
		if self.dbg:
			print(bgre(self.encrypt))
		recvs = self.keylist()
		if self.recvs:
			recvs = self.recvs
		if 'recipients' in kwargs.keys():
			recvs = kwargs['recipients']
		if not recvs:
			self.genkeys()
		recvs = ''.join(['-r %s'%r for r in recvs])
		out = '' if 'output' not in kwargs.keys() else '-o %s'%kwargs['output']
		gsc = '%s -e --armor --disable-policy-checks --disable-crl-checks ' \
            '%s %s'%(self._gsmbin, out, recvs)
		__crypt = cmd.stdo(gsc, inputs=message.encode())
		if __crypt:
			return __crypt.decode()
		return False

	def decrypt(self, message, output=None):
		"""text decrypting method"""
		if self.dbg:
			print(bgre(self.decrypt))
		out = '' if not output else '-o %s'%'output'
		gsc = '%s -d %s'%(self._gsmbin, out)
		__plain = cmd.stdo(gsc, inputs=message)
		if __plain:
			return __plain
		return False

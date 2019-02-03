#!/usr/bin/env python3
"""ssh connection and remote command """

#global imports"""
import os
import sys
import socket
from shutil import copy2
from socket import \
    gaierror as NameResolveError, timeout as sockettimeout
from psutil import Process

from paramiko import \
    ssh_exception, SSHClient, \
    AutoAddPolicy, SSHException

from colortext import bgre, tabd, abort, error
from system import whoami, userfind, filetime, setfiletime, filerotate
from executor import Command
from net import askdns

# default vars
__version__ = '0.1'

class SecureSHell(Command):
	"""paramiko wrapper class"""
	dbg = None
	reuser = whoami()
	remote = ''
	__ssh = None
	def __init__(self, *args, **kwargs):
		"""ssh init function"""
		for arg in args:
			if hasattr(self, arg):
				setattr(self, arg, True)
		for (key, val) in kwargs.items():
			if hasattr(self, key):
				setattr(self, key, val)
		if not 'timeout' in kwargs.keys():
			kwargs['tmeout'] = 3
		Command.__init__(self, *args, **kwargs)
		if self.dbg:
			print(bgre(SecureSHell.__mro__))
			print(bgre(tabd(self.__dict__, 2)))

	def _ssh(self, remote, reuser=None, port=22):
		"""ssh connector method"""
		if self.__ssh: return self.__ssh
		remote = remote if remote else self.remote
		reuser = reuser if reuser else self.reuser
		if '@' in remote:
			reuser, remote = remote.split('@')
		reuser = whoami() if not reuser else reuser
		if self.dbg:
			print(bgre('%s\n  %s@%s:%s '%(
                self._ssh, reuser, remote, port)))
		self.__ssh = SSHClient()
		self.__ssh.set_missing_host_key_policy(AutoAddPolicy())
		try:
			self.__ssh.connect(
                remote, int(port),
                username=reuser, allow_agent=True, look_for_keys=True)
		except (ssh_exception.SSHException, socket.gaierror) as err:
			error(self._ssh, err)
		return self.__ssh

	def rrun(self, cmd, remote=None, reuser=None):
		"""remote run method"""
		if self.dbg:
			print(bgre(self.rstdo))
			print(bgre('  %s@%s %s'%(reuser, remote, cmd)))
		ssh = self._ssh(remote, reuser)
		try:
			ssh.exec_command(cmd)
		except (AttributeError, ssh_exception.SSHException) as err:
			error(self.rrun, err)

	def rcall(self, cmd, remote=None, reuser=None):
		"""remote call method"""
		if self.dbg:
			print(bgre(self.rcall))
			print(bgre('  %s@%s %s'%(reuser, remote, cmd)))
		ssh = self._ssh(remote, reuser)
		try:
			chn = ssh.get_transport().open_session()
			chn.settimeout(10800)
			chn.exec_command(cmd)
			while not chn.exit_status_ready():
				if chn.recv_ready():
					och = chn.recv(1024)
					while och:
						sys.stdout.write(och.decode())
						och = chn.recv(1024)
				if chn.recv_stderr_ready():
					ech = chn.recv_stderr(1024)
					while ech:
						sys.stderr.write(ech.decode())
						ech = chn.recv_stderr(1024)
			return int(chn.recv_exit_status())
		except (
            AttributeError, ssh_exception.SSHException, socket.timeout) as err:
			error(self.rcall, err)
		except KeyboardInterrupt:
			abort()

	def rstdx(self, cmd, remote=None, reuser=None):
		"""remote stout/error method"""
		if self.dbg:
			print(bgre(self.rstdo))
			print(bgre('  %s@%s %s'%(reuser, remote, cmd)))
		ssh = self._ssh(remote, reuser)
		try:
			_, out, err = ssh.exec_command(cmd)
		except (AttributeError, ssh_exception.SSHException) as err:
			error(self.rstdx, err)
		return ''.join(out.readlines()), ''.join(err.readlines())

	def rstdo(self, cmd, remote=None, reuser=None):
		"""remote stdout method"""
		if self.dbg:
			print(bgre(self.rstdo))
			print(bgre('  %s@%s %s'%(reuser, remote, cmd)))
		ssh = self._ssh(remote, reuser)
		try:
			_, out, _ = ssh.exec_command(cmd)
		except (AttributeError, ssh_exception.SSHException) as err:
			error(self.rstdo, err)
			raise err
		return ''.join(out.readlines())

	def rstde(self, cmd, remote=None, reuser=None):
		"""remote stderr method"""
		if self.dbg:
			print(bgre(self.rstdo))
			print(bgre('  %s@%s %s'%(reuser, remote, cmd)))
		ssh = self._ssh(remote, reuser)
		try:
			_, _, err = ssh.exec_command(cmd)
		except (AttributeError, ssh_exception.SSHException) as err:
			error(self.rstde, err)
		return ''.join(err.readlines())

	def rerno(self, cmd, remote=None, reuser=None):
		"""remote error code  method"""
		if self.dbg:
			print(bgre(self.rerno))
			print(bgre('  %s@%s %s'%(reuser, remote, cmd)))
		ssh = self._ssh(remote, reuser)
		try:
			_, out, _ = ssh.exec_command(cmd)
		except (AttributeError, ssh_exception.SSHException) as err:
			error(self.rerno, err)
		return int(out.channel.recv_exit_status())

	def roerc(self, cmd, remote=None, reuser=None):
		"""remote stdout/stderr/errorcode method"""
		if self.dbg:
			print(bgre(self.rstdo))
			print(bgre('  %s@%s %s'%(reuser, remote, cmd)))
		ssh = self._ssh(remote, reuser)
		try:
			_, out, err = ssh.exec_command(cmd)
		except (AttributeError, ssh_exception.SSHException) as err:
			error(self.roerc, err)
		return ''.join(out.readlines()), ''.join(err.readlines()), \
            out.channel.recv_exit_status()

	def get(self, src, trg, remote=None, reuser=None):
		"""sftp get method"""
		if self.dbg:
			print(bgre(self.get))
			print(bgre('  %s@%s:%s %s'%(reuser, remote, src, trg)))
		if not os.path.isfile(src):
			raise FileNotFoundError('connot find either %s nor %s'%(src, trg))
		try:
			self.erno('scp %s@%s:%s %s'%(reuser, remote, src, trg)) == 0
		except FileNotFoundError:
			return False
		else:
			return True
	def put(self, src, trg, remote=None, reuser=None):
		"""sftp put method"""
		if self.dbg:
			print(bgre(self.put))
			print(bgre('  %s@%s:%s %s'%(reuser, remote, src, trg)))
		if not os.path.isfile(src):
			raise FileNotFoundError('connot find file %s'%src)
		try:
			self.erno('scp %s %s@%s:%s'%(src, reuser, remote, trg)) == 0
		except FileNotFoundError:
			return False
		else:
			return True

	def rcompstats(self, src, trg, remote=None, reuser=None):
		"""remote file-stats compare """
		smt = int(os.stat(src).st_mtime)
		if self.dbg:
			print(bgre(self.rcompstats))
			print(bgre('  %s@%s:%s %s'%(reuser, remote, src, trg)))
		rmt = self.rstdo(
            'stat -c %%Y %s'%trg, remote=remote, reuser=reuser)
		if rmt:
			rmt = int(str(rmt))
		srctrg = src, '%s@%s:%s'%(reuser, remote, trg)
		if rmt == smt:
			srctrg = False
		elif rmt and int(rmt) > int(smt):
			srctrg = '%s@%s:%s'%(reuser, remote, trg), src
		return srctrg

	def rfiletime(self, trg, remote=None, reuser=None):
		"""remote file-timestamp method"""
		if self.dbg:
			print(bgre(self.rfiletime))
			print(bgre('  %s@%s %s'%(remote, reuser, trg)))
		tamt = self.rstdo(
            'stat -c "%%X %%Y" %s'%trg, remote, reuser)
		tat = 0
		tmt = 0
		if tamt:
			tat, tmt = tamt.strip().split(' ')
		return int(tmt), int(tat)

	def rsetfiletime(self, trg, mtime, atime, remote=None, reuser=None):
		"""remote file-timestamp set method"""
		if self.dbg:
			print(bgre(self.rsetfiletime))
			print(bgre('  %s@%s %s %s %d'%(reuser, remote, trg, mtime, atime)))
		self.rstdo(
            'touch -m --date=@%s %s'%(mtime, trg), remote, reuser)
		self.rstdo(
            'touch -a --date=@%s %s'%(atime, trg), remote, reuser)

	def rfilerotate(self, lfile, remote, reuser):
		for i in range(1, int(rotate)):
			fi = '%s.%s'%(lfile, i)
			if exists(lfile):
				self.put(lfile, lfile, remote, reuser)

	def scpcompstats(self, lfile, rfile, rotate=0, remote=None, reuser=None):
		"""
		remote/local file compare method copying and
		setting the file/timestamp of the neweer one
		"""
		if self.dbg:
			print(bgre(self.scpcompstats))
			print(bgre('  %s@%s:%s %s'%(reuser, remote, rfile, lfile)))
		try:
			lmt, lat = filetime(lfile)
			rmt, rat = self.rfiletime(rfile, remote, reuser)
			if rmt == lmt:
				return False
			if rotate > 0:
				filerotate(lfile, rotate)
			if rmt and rmt > lmt:
				copy2(lfile, '%s.1'%lfile)
				self.get(rfile, lfile, remote, reuser)
				setfiletime(lfile, rmt, rat)
			elif lmt and lmt > rmt:
				self.put(lfile, rfile, remote, reuser)
				self.rsetfiletime(rfile, lmt, lat, remote, reuser)
		except SSHException as err:
			error(err)
		return True



if __name__ == '__main__':
	exit(1)

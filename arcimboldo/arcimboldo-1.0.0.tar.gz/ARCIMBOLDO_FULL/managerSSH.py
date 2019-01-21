#! /usr/bin/env python

#! /usr/bin/env python
# -*- coding: utf-8 -*-

#future imports and compatibility between 2.x and 3.x
from __future__ import print_function
from __future__ import division
#from __future__ import unicode_literals

import sys
info_p = sys.version_info
info_g = (sys.version).splitlines()
PYTHON_V =  info_p.major

if PYTHON_V == 3:
    from builtins import input

import warnings

warnings.simplefilter("ignore", DeprecationWarning)
warnings.simplefilter("ignore", UserWarning)

import os
import tempfile
import paramiko
import threading
import time


class Connection(object):
    """Connects and logs into the specified hostname.
    Arguments that are not given are guessed from the environment."""

    def __init__(self,
                 host,
                 username=None,
                 private_key=None,
                 password=None,
                 port=22,
                 ):
        self._sftp_live = False
        self._sftp = None
        self._first_sent = False
        self.lock = threading.Lock()
        if not username:
            username = os.environ['LOGNAME']

        # Log to a temporary file.
        templog = tempfile.mkstemp('.txt', 'ssh-')[1]
        paramiko.util.log_to_file(templog)

        # Begin the SSH transport.
        self._transport = paramiko.Transport((host, port))
        self._tranport_live = True
        # Authenticate the transport.
        if password:
            # Using Password.
            self._transport.connect(username=username, password=password)
        else:
            # Use Private Key.
            if not private_key:
                # Try to use default key.
                if os.path.exists(os.path.join(os.getenv("HOME"), './.ssh/id_rsa')):
                    private_key = os.path.join(os.getenv("HOME"), './.ssh/id_rsa')
                else:
                    raise TypeError("You have not specified a password or key.")

            private_key_file = os.path.expanduser(private_key)
            rsa_key = paramiko.RSAKey.from_private_key_file(private_key_file)
            self._transport.connect(username=username, pkey=rsa_key)

    def _sftp_connect(self):
        """Establish the SFTP connection."""
        if not self._sftp_live:
            self._sftp = paramiko.SFTPClient.from_transport(self._transport)
            self._sftp_live = True
        return self._sftp

    def get(self, sftpconn, remotepath, localpath=None):
        """Copies a file between the remote host and the local host."""
        if not localpath:
            localpath = os.path.split(remotepath)[1]
        sftpconn.get(remotepath, localpath)

    def put(self, sftpconn, localpath, remotepath=None):
        """Copies a file between the local host and the remote host."""
        if not remotepath:
            remotepath = os.path.split(localpath)[1]
        sftpconn.put(localpath, remotepath)

    def execute(self, command):
        """Execute the given commands on a remote machine."""
        channel = self._transport.open_session()
        channel.exec_command(command)
        output = channel.makefile('rb', -1).readlines()
        if output:
            channel.close()
            return output
        else:
            error = channel.makefile_stderr('rb', -1).readlines()
            channel.close()
            return error

    def interactive(self):
        channel = self._transport.open_session()
        channel.get_pty()
        channel.invoke_shell()
        return channel

    def send_command_to_channel(self, channel, command, termination, stopif=None):
        self.lock.acquire()
        if command[-1] != "\n":
            command += "\n"

        buff = ""
        volte = 0
        if not self._first_sent:
            if stopif != None:
                while not buff.endswith(termination) and not buff.endswith(stopif):
                    if len(buff) == 0 and volte > 1:
                        break
                    if channel.recv_ready():
                        resp = channel.recv(9999)
                        resp = resp.replace(" \r", "")
                    else:
                        volte += 1
                        time.sleep(1)
                        resp = ""
                    buff += resp
                    # print "|||||||||||"
                    # print buff
                    # print "|||||||||||"
                    # print termination,stopif
                    buff = ""
            else:
                while not buff.endswith(termination):
                    if len(buff) == 0 and volte > 1:
                        break
                    if channel.recv_ready():
                        resp = channel.recv(9999)
                        resp = resp.replace(" \r", "")
                    else:
                        volte += 1
                        time.sleep(1)
                        resp = ""
                    buff += resp
                    buff = ""
                    # print "|||||||||||"
                    # print buff,command,termination
                    # print "|||||||||||"
            self._first_sent = True

        channel.send(command)
        buff = ''
        while not buff.endswith(termination):
            resp = channel.recv(9999)
            resp = resp.replace(" \r", "")
            buff += resp
            # print buff
            if stopif != None:
                if buff.endswith(stopif):
                    self.lock.release()
                    # print "*************************"
                    # print buff
                    # print "*************************"
                    return (buff, True)
                    # print list(buff[-3:]),buff[-10:]
                    # print buff.endswith(termination), termination, buff[-2:] == termination, len(buff[-2:]), len(termination),buff[-2],termination[-2],buff[-2]==termination[-2],buff[-1],termination[-1],buff[-1]==termination[-1]
        # print "================================"
        # print buff
        # sys.stdout.flush()
        burr = buff.splitlines()
        buff = ""
        for li in burr:
            if len(li.strip()) != 0:
                buff += li + "\n"
        self.lock.release()
        # print "*************************"
        # print buff
        # print "*************************"
        return buff

    def open_sublocal_interactive_ssh(self, user, host, port, password, prompt, channel=None):
        if channel == None:
            cha = self.interactive()
        else:
            cha = channel
        # print "Invio signal","ssh -p "+str(port)+" "+user+"@"+host+"\n"
        buff = self.send_command_to_channel(cha, "ssh -p " + str(port) + " " + user + "@" + host + "\n",
                                            '\'s password: ', stopif=prompt)
        # print "ended"
        if not isinstance(buff, tuple):
            buff += self.send_command_to_channel(cha, password + "\n", prompt, stopif='\'s password: ')
        else:
            buff = buff[0]
        return cha, buff

    def open_sftp_channel(self):
        sftpconn = self._sftp_connect()
        return sftpconn

    def close(self):
        """Closes the connection and cleans up."""
        # Close SFTP Connection.
        if self._sftp_live:
            self._sftp.close()
            self._sftp_live = False
        # Close the SSH Transport.
        if self._tranport_live:
            self._transport.close()
            self._tranport_live = False

    def __del__(self):
        """Attempt to clean up if not explicitly closed."""
        self.close()

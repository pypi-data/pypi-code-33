# -*- coding: utf-8 -*-

"""Main module."""

import logging
import getpass
import keyring
import pybis

class Iportal(object):
    """Main portal class"""

    def __init__(self,username,password,url): # ,datamover_dir
        self.username = username
        self._password = password
        self.url = url

    def write(self,arg1='arg1_default'):
        print("Write: %s"%(arg1))

    def read(self):
        print("Read: %s"%(self.username))

    def adduser(self):
        print("adduser")

    def configure(self):
        print("configure")

    def status(self):
        print("status")

    def start(self):
        print("start")

    def stop(self):
        print("stop")

    def addcron(self):
        print("addcron")

    def build(self):
        print("build")

    def cp(self):
        print("cp")

    def test(self):
        print("test")

    def submit(self):
        print("submit")

    def ls(self):
        print("ls")

    @staticmethod
    def parse_connection(connection):
        (username,url) = connection.split("@")
        password = keyring.get_password(username,url)
        if not password:
            password = getpass.getpass()
            keyring.set_password(username,url,password)
        return username,url,password

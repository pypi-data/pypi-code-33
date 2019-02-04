# -*- coding: utf-8 -*-

"""Main module."""

import logging

class Iportal(object):
    """Main portal class"""

    def __init__(self,username,password,url,datamover_dir,dssrc):
        self.username = username
        self.password = password
        self.url = url
        self.datamover_dir = datamover_dir
        self.dssrc = dssrc

    def ping(self):
        print("ping")

    @staticmethod
    def read_dssrc(dssrc):
        if not dssrc:
            raise ValueError("Needs either -r dssrc.ini OR -u <username> -p <password> -i <url> -d <datamover_dir>")
        logging.warning("Reading %s"%(dssrc))
        read_data = {}
        with open(dssrc,"r") as dssrc_fh:
            for line in dssrc_fh:
                if line.startswith("#"):
                    continue
                elif line.find("=") < 0:
                    continue
                (key,value) = line.split("=",1)
                read_data[key.strip()] = value.strip()
        return (read_data['username'],read_data['password'],read_data['url'],read_data['datamover_dir'])

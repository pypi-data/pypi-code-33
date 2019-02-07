#! /usr/bin/env python

"""
WorkSpace Component Configurations
"""

import  os                    as _os
from pyspark import SparkConf as _SparkConf
import subprocess             as _subprocess

from bgg.imp import Imp       as _Imp
from bgg.sp  import sp        as _sp

_imp = _Imp(self.impylaConf)

_IMPALA_CLI_LIST=["impala-shell", "-Vks", "impala", 
                  "-i", "bdpimp02-gf1.pncint.net",  "--ssl",
                  "-d", "bdahd01p_dlapd1_apd_fraud_aml"]

_HIVE_CONN="'jdbc:hive2://bdphiv02-gf1.pncint.net:10000"
_HIVE_CONN+="/bdahd01p_dlapd1_apd_fraud_aml;"
_HIVE_CONN+="principal=hive/bdphiv02-gf1.pncint.net@PROD.PNCINT.NET;"
_HIVE_CONN+="ssl=true'"

_HIVE_CLI_LIST=["beeline","-u",_HIVE_CONN,
                          "--hiveconf","mapred.job.queue.name=root.bda.high"]

class BggConf(object):

    """
    Configuration for a BGG application. Used to set various CDH &
    Spark parameters as key-value pairs.
    Similar to SparkConf, all setter methods in this class support chaining.
    """
    def __init__(self):
        """
        Create a new BGG configuration.

        """
        self._setDataConf()
        self._setImpylaConf()
        self._setSparkConf()
        
    def _setDataConf(self):
        HDFS_PATH_DB="/user/"+_os.environ["HADOOP_USER_NAME"]+"/bgg" \
                    if "HADOOP_USER_NAME" in _os.environ.keys() else \
                    "/user/hive/warehouse/bgg.db/"
        LOCAL_PATH_DATA=_os.getcwd()+"/data"
        self.dataConf={
         "REMOTE_URL_TOP":'http://ratiocinate.com/bgg/data/top.csv',
         "REMOTE_URL_HEADER":'http://ratiocinate.com/bgg/data/header.csv',
         "REMOTE_URL_RATING":'http://ratiocinate.com/bgg/data/rating.csv',
         "LOCAL_PATH_DATA":LOCAL_PATH_DATA,
         "LOCAL_PATH_TOP":LOCAL_PATH_DATA + "/top",
         "LOCAL_PATH_HEADER":LOCAL_PATH_DATA + "/header",
         "LOCAL_PATH_RATING":LOCAL_PATH_DATA + "/rating",
         "BGG_DB_NAME":"bgg",
         "HDFS_PATH_DB":HDFS_PATH_DB,
         "HDFS_PATH_TOP_RAW":HDFS_PATH_DB + "/top_raw",
         "HDFS_PATH_TOP":HDFS_PATH_DB + "/top",
         "HDFS_PATH_HEADER_RAW":HDFS_PATH_DB + "/header_raw",
         "HDFS_PATH_HEADER":HDFS_PATH_DB + "/header",
         "HDFS_PATH_RATING_RAW":HDFS_PATH_DB + "/rating_raw",
         "HDFS_PATH_GAME":HDFS_PATH_DB + "/game",
         "HDFS_PATH_RATING_RAW":HDFS_PATH_DB + "/rating_raw",
         "HDFS_PATH_RATING_RAW":HDFS_PATH_DB + "/rating_raw",
         "HDFS_PATH_RATING":HDFS_PATH_DB + "/rating",
         "HDFS_PATH_PREDCV":HDFS_PATH_DB + "/predcv",
         "HDFS_PATH_PRED":HDFS_PATH_DB + "/pred",
         "HDFS_PATH_EVAL":HDFS_PATH_DB + "/eval",
         "HDFS_PATH_MDL":HDFS_PATH_DB + "/mdl"}    
        
    def _setImpylaConf(self):
        host = _os.environ["IMPALA_HOST"] \
                if "IMPALA_HOST" in _os.environ.keys() else ""    
        port = _os.environ["IMPALA_PORT"] \
                if "IMPALA_HOST" in _os.environ.keys() else "21050"
        user = _os.environ["HADOOP_USER_NAME"] \
                if "HADOOP_USER_NAME" in _os.environ.keys() else ""    
        cmd = ['hdfs','dfs','-cat','/user/%s/.password' % user]
        sp = _subprocess.Popen(cmd, stdout=_subprocess.PIPE)
        password = sp.communicate()[0]
        db = self.bggConf["BGG_DB_NAME"]
        self.impylaConf={"kerberos_service_name":'impala',"ldap_password":None,
                         "auth_mechanism":'NOSASL',"use_ldap":None,"user":user,
                         "ca_cert":None,"timeout":None,"host":host,"port":port,
                         "password":password,"ldap_user":None,"protocol":None,
                         "use_kerberos":None,"database":db,"use_ssl":False}
    
    def _setSparkConf(self):
        self.sparkConf = _SparkConf()\
                         .setAppName("bgg")\
                         .set("spark.yarn.executor.memoryOverhead", "2048")


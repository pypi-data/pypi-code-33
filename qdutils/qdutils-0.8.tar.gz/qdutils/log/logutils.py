#  -*- coding: utf-8 -*-

'''

@desc: 
@author: tony
@Date: 2018/12/26 下午4:58

'''
import os
import traceback
import time
import logging
import logging.handlers
from logging.handlers import TimedRotatingFileHandler


class logutils(object):
    pass

    DEFAULT_LOG_PATH = '/tmp/python_app_log/'
    DEFAULT_LOG_FILE_NAME = 'app.log'

    def __init__(self):
        pass

    logger = None

    @staticmethod
    def getLogger(log_path, filename=DEFAULT_LOG_FILE_NAME, log_level=logging.INFO, when='H',
                  interval=1,
                  backupCount=0):
        """
        :param log_path: 日志路径 
        :param filename: 日志文件名 
        :param log_level: 日志级别 
        :param when: 日期时间切分级别
        # S - Seconds
        # M - Minutes
        # H - Hours
        # D - Days 
        :param interval: 间隔数 
        :param backupCount: 保留日志个数。默认的0是不会自动删除掉日志。若设10，则在文件的创建过程中
        库会判断是否有超过这个10，若超过，则会从最先创建的开始删除。 
        :return: logging对象
        """
        log_file_path = ''
        log_file = ''
        if not log_path:
            log_file_path = logutils.DEFAULT_LOG_PATH
        else:
            log_file_path = log_path
        log_file = os.path.join(log_file_path, filename)
        logutils.__create_path(log_file_path)
        # if logutils.logger is None:
        log_fmt = '%(asctime)s\tFile \"%(filename)s\",line %(lineno)s\t%(levelname)s: %(message)s'
        formatter = logging.Formatter(log_fmt)
        log_file_handler = TimedRotatingFileHandler(filename=log_file, when=when, interval=interval,
                                                    backupCount=backupCount)
        log_file_handler.setFormatter(formatter)
        logging.basicConfig(level=log_level, filename=log_file, filemode='a+',
                            format='%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s %(message)s',
                            datefmt='%a, %d %b %Y %H:%M:%S')
        log = logging.getLogger()
        log.addHandler(log_file_handler)
        # logutils.logger = logging

        return logging

    @staticmethod
    def __create_path(file_path):
        try:
            # tmp_file_path = str(file_path)[0:str(file_path).rfind('/')]
            tmp_file_path = file_path
            if not os.path.exists(tmp_file_path):
                os.makedirs(tmp_file_path)
        except Exception:
            raise RuntimeError('create_path is error:')
            # print 'create_path'
            # traceback.print_exc()

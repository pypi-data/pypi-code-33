import logging
import os
from logging.handlers import RotatingFileHandler, SysLogHandler


class Logger:
    def __init__(self, log_name):
        self.log_name = log_name
        pid = os.getpid()

        intexfy_env = os.getenv('INTEXFY_ENV')

        if intexfy_env == 'production':
            log_endpoint = 'prodlog.intexfy.com'
            self.log_file = '/var/log/intexfy_apps/%s_pid%s.log' % (
                self.log_name, pid)

        if intexfy_env == 'beta':
            log_endpoint = 'betalog.intexfy.com'
            self.log_file = '/var/log/intexfy_apps/%s_pid%s.log' % (
                self.log_name, pid)

        if intexfy_env == 'development':
            log_endpoint = 'localhost'
            self.log_file = '/var/log/intexfy_apps/%s_pid%s.log' % (
                self.log_name, pid)
        else:
            log_endpoint = 'localhost'
            self.log_file = './logs/%s_pid%s.log' % (self.log_name, pid)

        formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
        try:
            hdlr = RotatingFileHandler(self.log_file, mode='a',
                                       maxBytes=5 * 1024 * 1024,  # 5 Mb
                                       backupCount=10,
                                       encoding="UTF-8",
                                       delay=0)
        except FileNotFoundError:
            os.mkdir(os.path.dirname(self.log_file))
            hdlr = RotatingFileHandler(self.log_file, mode='a',
                                       maxBytes=5 * 1024 * 1024,  # 5 Mb
                                       backupCount=10,
                                       encoding="UTF-8",
                                       delay=0)

        # handler_v2 = SysLogHandler(address=(log_endpoint, 520))

        hdlr.setFormatter(formatter)
        # handler_v2.setFormatter(formatter)

        self.logger = logging.getLogger(self.log_name)
        self.logger.addHandler(hdlr)
        # self.logger.addHandler(handler_v2)
        self.logger.setLevel(logging.DEBUG)

    def debug(self, instance, string):
        self.logger.debug('[Ins: %s] %s', instance, string)

    def info(self, instance, string):
        self.logger.info('[Ins: %s] %s', instance, string)

    def warn(self, instance, string):
        self.logger.warning('[Ins: %s] %s', instance, string)

    def error(self, instance, string):
        self.logger.error('[Ins: %s] %s', instance, string)

    def exception(self, instance, string):
        self.logger.exception('[Ins: %s] %s', instance, string)


# class Logger2:
#     def __init__(self, log_name):
#         self.log_name = log_name
#
#         host = 'localhost'
#
#         hdlr = logstash.TCPLogstashHandler(host, 5959)
#
#         self.logger = logging.getLogger(self.log_name)
#         self.logger.addHandler(hdlr)
#         self.logger.setLevel(logging.DEBUG)
#
#     def debug(self, instance, string):
#         self.logger.debug('[Ins: %s] %s' % (instance, string))
#
#     def info(self, instance, string):
#         self.logger.info('[Ins: %s] %s' % (instance, string))
#
#     def warn(self, instance, string):
#         self.logger.warning('[Ins: %s] %s' % (instance, string))
#
#     def error(self, instance, string):
#         self.logger.error('[Ins: %s] %s' % (instance, string))

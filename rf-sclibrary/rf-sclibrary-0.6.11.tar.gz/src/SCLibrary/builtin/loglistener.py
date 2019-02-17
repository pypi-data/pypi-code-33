# -*- coding:utf-8 -*-
import re

class LogListener(object):
    ROBOT_LISTENER_API_VERSION = 2

    # def start_suite(self, name, args):
    # print "Starting Suite : " + args['source']

    # def start_test(self, name, args):
    # print "Starting test : " + name
    # if args['template']:
    #     print 'Template is : ' + args['template']

    # def end_test(self, name, args):
    # print "Ending test:  " + args['longname']
    # print "Test Result is : " + args['status']
    # print "Test Time is: " + str(args['elapsedtime'])

    def __init__(self):
        self.pre_log = ''

    def log_message(self, message):
        if  message['message'] == self.pre_log and message['level']=='INFO' and re.search(r'^\${.+}\s=\s', self.pre_log, flags=0) is not None:
            return

        if(message['message'].startswith('INFO :')):
            print("\n" + message['message'])
            return

        if message['level'] == 'FAIL':
            print("\n\033[31m" + message['level'] + " : " + message['message'] + '\033[0m')
        else:
            print("\n" + message['level'] + " : " + message['message'])
        self.pre_log =  message['message']
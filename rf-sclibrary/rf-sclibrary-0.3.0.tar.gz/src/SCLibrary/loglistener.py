# -*- coding:utf-8 -*-

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

    def log_message(self, message):
        if(message['message'].encode('utf-8').startswith('INFO :')):
            print "\n" + message['message'].encode('utf-8')
            return
        print "\n" + message['level'] + " : " + \
            message['message'].encode('utf-8')

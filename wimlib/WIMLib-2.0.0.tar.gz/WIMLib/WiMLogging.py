#------------------------------------------------------------------------------
#----- Logging.py ------------------------------------------------------------
#------------------------------------------------------------------------------
#
#  copyright:  2016 WiM - USGS
#
#    authors:  Jeremy K. Newson - USGS Web Informatics and Mapping (WiM)
#              
#    purpose:  A simple log tracking application for StreamStats.
#
#      usage:  THIS SECTION NEEDS TO BE UPDATED
#
# discussion:  THIS SECTION NEEDS TO BE UPDATED
#
#      dates:   05 NOV 2016 jkn - Created / Date notation edited by jw
#               04 APR 2017 jw - Modified
#
#------------------------------------------------------------------------------

#region "Imports"
import os
import logging
#endregion

class WiMLogging:
    class __WiMLogging:
        def __init__(self,logdir=None):
            self.CanLogToFile = False
            self.LogMessages =[]
            if (not logdir == None): 
                self.CanLogToFile =True
                logging.basicConfig(filename=logdir, format ='%(asctime)s %(message)s', level=logging.DEBUG)


    instance = None
    def __init__(self, logpath = None, fileName = "log.log"):
        if not WiMLogging.instance:
            dir = None
            if not logpath == None:
                if not os.path.exists(logpath):
                    os.makedirs(logpath)     
                dir = os.path.join(logpath, fileName)
        
            WiMLogging.instance = WiMLogging.__WiMLogging(dir)


    def sm(self, msg, type="INFO", errorID=0):
        self.instance.LogMessages.append(type +':' + msg.replace('_',' '))
    #     print(type +' ' + str(errorID) + ' ' + msg)
        if (self.instance.CanLogToFile):
            if type in ('ERROR'): logging.error(str(errorID) +' ' + msg)
            else : logging.info(msg)
        else:
            print (type, msg)

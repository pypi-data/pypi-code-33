#!/usr/bin/env python3
# -*- coding: utf-8 -*-

### Kryptic Studio ###

# Local Libraries

# Libraries

# Standard Libraries
import time
from sty import fg, bg, ef, rs
# Global Variables

# Function Definitions

def timeLocal():
        localtime = time.asctime(time.localtime(time.time()) )
        return(localtime)


class log(object):
    @staticmethod
    def info(message, log = True, write = False, time = False):
        
        logData = fg.cyan + "[INFO] " + fg.rs + message 
        logDataW = "[INFO] " + message 
        if time == True:
            time = "[" + timeLocal() + "] "
            logData =  time + logData
            logDataW = time + logDataW
        if log == True:
                print(logData)
        if write == True:
            logFile = open("KrypticLogger/Logs/log.txt", "a")
            logFile.write(logDataW + "\n")
            logFile.close()

    @staticmethod
    def error(message, log = True, write = False, time = False, code = "", critical = False):
        
        logData = fg.red + "[ERROR] " + fg.rs + message
        logDataW = "[ERROR] " + message
        if code != "":
            logData = fg.red + "[ERROR] " + fg.rs + message + "\n\tError: " + code
            logDataW = "[ERROR] " + message + "\n\tError: " + code
        if critical == True:
            logData += fg.red + "\tCRITICAL" + fg.rs
            logDataW += "\tCRITICAL"
        if time == True:
            time = "[" + timeLocal() + "] "
            logData =  time + logData
            logDataW = time + logDataW
        if log == True:
                print(logData)
        if write == True:
            logFile = open("KrypticLogger/Logs/log.txt", "a")
            logFile.write(logDataW + "\n")
            logFile.close()

    @staticmethod
    def success(message, log = True, write = False, time = False):
        
        logData = fg.green + "[SUCCESS] " + fg.rs + message
        logDataW = "[SUCCESS] " + message
        if time == True:
            time = "[" + timeLocal() + "] "
            logData =  time + logData
            logDataW = time + logDataW
        if log == True:
                print(logData)
        if write == True:
            logFile = open("KrypticLogger/Logs/log.txt", "a")
            logFile.write(logDataW + "\n")
            logFile.close()

    @staticmethod
    def warn(message, log = True, write = False, time = False):
        
        logData = fg.yellow + "[WARNING] " + fg.rs + message
        logDataW = "[WARNING] " + message
        if time == True:
            time = "[" + timeLocal() + "] "
            logData =  time + logData
            logDataW = time + logDataW
        if log == True:
                print(logData)
        if write == True:
            logFile = open("KrypticLogger/Logs/log.txt", "a")
            logFile.write(logDataW + "\n")
            logFile.close()

    @staticmethod
    def log(message, log = True, write = False, time = False):
        
        logData = fg.white + "[LOG] " + fg.rs + message
        logDataW = "[LOG] " + message
        if time == True:
            time = "[" + timeLocal() + "] "
            logData =  time + logData
            logDataW = time + logDataW
        if log == True:
                print(logData)
        if write == True:
            logFile = open("KrypticLogger/Logs/log.txt", "a")
            logFile.write(logDataW + "\n")
            logFile.close()

    @staticmethod
    def debug(message, log = True, write = False, time = False):
        
        logData = fg.blue + "[DEBUG] " + fg.rs + message
        logDataW = "[DEBUG] " + message
        if time == True:
            time = "[" + timeLocal() + "] "
            logData =  time + logData
            logDataW = time + logDataW
        if log == True:
                print(logData)
        if write == True:
            logFile = open("KrypticLogger/Logs/log.txt", "a")
            logFile.write(logDataW + "\n")
            logFile.close()

    @staticmethod
    def track(message, log = True, write = False, time = False):
        
        logData =  fg.black + "[TRACK] " + fg.rs + message
        logDataW = "[TRACK] " + message
        if time == True:
            time = "[" + timeLocal() + "] "
            logData =  time + logData
            logDataW = time + logDataW
        if log == True:
                print(logData)
        if write == True:
            logFile = open("KrypticLogger/Logs/log.txt", "a")
            logFile.write(logDataW + "\n")
            logFile.close()

# Main Function Definition

# Main Function Definition
#def main(): ### Uncomment if nessesary!
#    return ### Uncomment if nessesary!
# Call to main()
#main() ### Uncomment if nessesary!

#or

#if __name__ == '__main__': ### Uncomment if nessesary!
#    main() ### Uncomment if nessesary!
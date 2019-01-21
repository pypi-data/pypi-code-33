
#Extands logging with a trace level

#Idea from https://stackoverflow.com/questions/2183233/how-to-add-a-custom-loglevel-to-pythons-logging-facility

from logging import *

import logging

TRACE = 5 

logging.addLevelName(TRACE, "TRACE")

def trace(self, message, *args, **kws):
    if self.isEnabledFor(TRACE):
        self._log(TRACE, message, args, **kws) 
logging.Logger.trace = trace


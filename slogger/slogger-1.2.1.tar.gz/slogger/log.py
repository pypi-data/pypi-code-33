import logging
import os
import sys
from .util import buildLogContent
from .handler import loadHandlers

class _Logger:
    def __init__(master):
        def getLogger(category):
            class pureLogger:
                def __init__(self, title = None):
                    self.logger = loadHandlers(logging.getLogger(category), category)
                    
                    def debug(obj):
                        self.logger.debug(buildLogContent(title, obj))
                        return obj

                    def info(obj):
                        self.logger.info(buildLogContent(title, obj))
                        return obj

                    def error(obj):
                        self.logger.error(buildLogContent(title, obj))
                        return obj

                    def warning(obj):
                        self.logger.warning(buildLogContent(title, obj))
                        return obj

                    self.debug = debug
                    self.info = info
                    self.error = error
                    self.warning = warning
                    
            class innerLogger:
                def __init__(self):
                    _pureLogger = pureLogger()

                    self.debug = _pureLogger.debug
                    self.info = _pureLogger.info
                    self.error = _pureLogger.error
                    self.warning = _pureLogger.warning

                    def title(title):
                        return pureLogger(title)

                    self.title = title
                    
            return innerLogger()
        
        master.getLogger = getLogger
        
        

Logger = _Logger()

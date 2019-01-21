import collections
import sys
from timeit import default_timer as timer
import os
import logging
from logging.handlers import TimedRotatingFileHandler as TimedHandler
import logging.handlers as loghandlers
import functools
from python_log_indenter import IndentedLoggerAdapter
from datetime import datetime
from .locations import get_name,create_path,Folder,InfoDict

def create_filter(filter_func,*args,filter_name='',**kwargs):
	class CustomFilter(logging.Filter):
		
		def filter(self,record):
			return filter_func(record.getMessage(),*args,**kwargs)
	
	return CustomFilter(filter_name)

logging.INFORM=INFORM=369
logging.addLevelName(INFORM,"INFORM")

def inform(self,message,*args,**kws):
	# Yes, logger takes its '*args' as 'args'.
	if self.isEnabledFor(INFORM):
		self._log(INFORM,message,args,**kws)

logging.Logger.inform=inform

# region level_mapper:
level_mapper=dict()
level_mapper[logging.DEBUG]=lambda some_logger:some_logger.debug
level_mapper[logging.INFO]=lambda some_logger:some_logger.info
level_mapper[logging.WARNING]=lambda some_logger:some_logger.warning
level_mapper[logging.ERROR]=lambda some_logger:some_logger.error
level_mapper[logging.CRITICAL]=lambda some_logger:some_logger.critical
level_mapper[logging.INFORM]=lambda some_logger:some_logger.inform

# endregion
#todo:Group log files into folder. After expiration, delete folder (if left empty after cleaning).

class TheLogger(IndentedLoggerAdapter):
	
	def __init__(self,name,_log_folder=None,level=logging.DEBUG,log_format=None,to_stream=True,**kwargs):
		super(TheLogger,self).__init__(logging.Logger(name,level),**dict(dict(spaces=1,indent_char='|---'),**kwargs))
		self.log_folder: Folder=_log_folder or log_folder
		self.formatter=logging.Formatter(log_format or simple_fmt)
		if to_stream: self.addHandler(logging.StreamHandler())
	
	def addHandler(self,logHandler,level=None,log_format=None):
		logHandler.setLevel(level or self.logger.level)
		if log_format is None: formatter=self.formatter
		else: formatter=logging.Formatter(log_format)
		logHandler.setFormatter(formatter)
		self.logger.addHandler(logHandler)
		return logHandler
	
	def add_timed_handler(self,filepath,when='d',interval=1,backupCount=14,level=None,
	                      log_format=None,**other_opts):
		# filepath=filepath or create_path(1,logs_dir,get_name(self.name)+'.log')
		return self.addHandler(loghandlers.TimedRotatingFileHandler(
			filename=filepath,when=when,interval=interval,backupCount=backupCount,**other_opts),
			level=level,log_format=log_format)
	
	def create_log_file(self,filename,include_depth=2,timing_opts=None,folder_parts=None,file_parts=None,**kwargs):
		fp=self.log_folder.create(file=get_name(filename),**(folder_parts or {}))\
			.get_filepath(include_depth=include_depth,pid=os.getpid(),include_datetime=True,**(file_parts or {}),**kwargs)
		self.add_timed_handler(fp,**(timing_opts or {}))
		self.info('log_filepath=%s',fp)
		self.inform('log_filepath=%s',fp)
		self.pop()
		return self
	
	def __getitem__(self,item):
		return level_mapper[item](self)
	
	def inform(self,msg,*args,**kwargs):
		self.logger.inform(msg,*args,**kwargs)
	
	def with_logging(self,log_level=logging.INFO):
		# if logger is None: logger=simple_logger
		# assert logger is not None
		logger_say=level_mapper[log_level](self)
		
		def second_wrapper(func):
			@functools.wraps(func)
			def wrapper(*args,**kwargs):
				logger_say('Running "%s":',func.__name__)
				self.add()
				
				start=timer()
				try:
					result=func(*args,**kwargs)
				except KeyboardInterrupt:
					logger_say('KeyboardInterrupt within %s. Duration: %s',
					           func.__name__,timer()-start)
					sys.exit()
				except Exception as e:
					logger_say(str(e),exc_info=True)
					raise e
				self.sub()
				logger_say('Done "%s". Duration: %.3f sec.',func.__name__,timer()-start)
				return result
			
			return wrapper
		
		return second_wrapper

log_fmt="%(asctime)s -- %(levelname)s -- %(name)s -- %(funcName)s -- %(filename)s -- %(lineno)d -- %(message)s"
simple_fmt="%(asctime)s|||pid:%(process)d|||%(levelname)s|||: %(message)s"
log_folder=None  #Folder('~').create('backend_logs')
logger=None  #TheLogger('simple_logger',log_folder)

def with_logging(log_level=logging.INFO):
	# global log_folder,logger
	# if log_folder is None: log_folder=Folder('~').create('backend_logs')
	# if logger is None: logger=TheLogger('simple_logger',log_folder)
	assert logger is not None, "Please, first create logger using create_logger(folder_path) method."
	return logger.with_logging(log_level)

# def get_logger_filepath(info: dict,dir_depth=1):
# 	kv_pairs=[f'{k}={v}' for k,v in info.items()]
# 	log_filename="___".join([*kv_pairs[dir_depth:],*kv_pairs[:dir_depth]])
# 	log_filepath=create_path(1,logs_folder.path,*kv_pairs[:dir_depth],log_filename+'.log')
# 	return log_filepath2

# simple_logger=TheLogger('simple_logger',)  #create_process_logger(__file__,collections.OrderedDict(pid=os.getpid()))

def create_logger(folder_path):
	global logger,log_folder
	log_folder=Folder(folder_path)
	logger=TheLogger('default_logger',log_folder)
	return logger

def main():
	return

if __name__=='__main__':
	main()
	pass

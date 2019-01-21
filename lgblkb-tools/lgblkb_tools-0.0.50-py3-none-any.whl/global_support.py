from pprint import pformat
import ruamel.yaml as raml
import uuid
import collections
import types
import pytz
from enum import Enum,auto
import multiprocessing as mp
from . import schedule
from abc import ABC
from functools import partial,partialmethod
import concurrent.futures
import rx
import signal
import sys
import time
from sklearn.preprocessing import MinMaxScaler
import numpy as np
from typing import Iterable,Callable,Sized,Dict,List
import zipfile
from datetime import date,timedelta,datetime
import os
import subprocess
import geojson
import pandas as pd
import dateutil.parser
# from .log_support import with_logging,INFORM
from . import log_support as logsup
from .locations import *
from .helpers import constrained_sequence

pd.set_option('max_colwidth',40)
pd.set_option('expand_frame_repr',False)

class AutoName(Enum):
	
	def _generate_next_value_(name,start,count,last_values):
		return name

def run_shell(*args,non_blocking=False,chdir=None,with_popen=False,ret_triggers=None,**kwargs):
	chdir=chdir or os.getcwd()
	normal_dir=os.getcwd()
	os.chdir(chdir)
	
	if non_blocking:
		subprocess.Popen(args,stdout=subprocess.PIPE,**kwargs)
	else:
		#output=subprocess.run(args,stdout=subprocess.PIPE,**kwargs).stdout.decode()
		#output=subprocess.run(args,stdout=subprocess.PIPE,**kwargs).stdout.decode()
		if with_popen:
			process=subprocess.Popen(args,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,preexec_fn=os.setsid)
			regular_termination=True
			nextline=''
			while regular_termination:
				nextline=process.stdout.readline().decode()
				# print('nextline:',nextline)
				if nextline=='' and process.poll() is not None:
					break
				if ret_triggers:
					for ret_trigger in ret_triggers:
						if ret_trigger in nextline:
							regular_termination=False
							break
				logsup.logger.debug(nextline)
				# sys.stdout.write(nextline)
				sys.stdout.flush()
			if regular_termination:
				output=process.communicate()[0]
				exitCode=process.returncode
				if exitCode!=0:
					raise Exception(args,exitCode,output)
			else:
				logsup.logger.info(r'Manual process termination triggered with line:\n%s',nextline)
				logsup.logger.debug('Killing process: %s',process.pid)
				os.killpg(os.getpgid(process.pid),signal.SIGTERM)
				raise Exception('Manual process termination.')
		else:
			subprocess.run(args,stdout=subprocess.PIPE,**kwargs).stdout.decode()
	os.chdir(normal_dir)

def period_within(days=None,start_date=None,end_date=None):
	if isinstance(start_date,str): start_date=dateutil.parser.parse(start_date)
	if isinstance(end_date,str): end_date=dateutil.parser.parse(end_date)
	if days is not None:
		if start_date is not None:
			end_date=start_date+timedelta(days=days)
		elif end_date is not None:
			start_date=end_date-timedelta(days=days)
		else:
			end_date=date.today()
			start_date=end_date-timedelta(days=days)
	else:
		end_date=end_date or date.today()
	return start_date,end_date

def datetime_within(start=None,end=None,**timedelta_opts):
	if timedelta_opts:
		if start is not None:
			end=start+timedelta(**timedelta_opts)
		elif end is not None:
			start=end-timedelta(**timedelta_opts)
		else:
			end=datetime.now()
			start=end-timedelta(**timedelta_opts)
	else:
		end=end or datetime.now()
	return start,end

def try_to_do(func,*args,check_success=None,max_attempts=5,max_wait_seconds=0,**kwargs):
	if check_success is None: check_success=lambda x:True
	max_attempts=max(max_attempts,1)
	if max_wait_seconds:
		waiting_times=constrained_sequence(max_attempts,lambda x:np.exp(x/4))
		waiting_times=MinMaxScaler((0,max_wait_seconds))\
			.fit_transform(np.array(waiting_times).reshape(-1,1))
	else: waiting_times=[0]*max_attempts
	logsup.logger.debug('Trying to accomplish "%s" ...',func.__name__)
	wait_time=iter(waiting_times)
	for i in range(max_attempts):
		time_to_wait=next(wait_time)
		if time_to_wait!=0: logsup.logger.info('Sleeping for %s sec.',time_to_wait)
		time.sleep(time_to_wait)
		logsup.logger.debug('Attempt #%s.',i+1)
		out=func(*args,**kwargs)
		# simple_logger.debug('check_success:')
		if check_success(out):
			logsup.logger.debug('Succeeded.')
			return out
		else:
			logsup.logger.info('Attempt #%s failed.',i+1)
	return False

def run_until_victory(func,retry_timeout,*args,**kwargs):
	manager=mp.Manager()
	res_dict=manager.dict()
	args=[res_dict,*args]
	count=0
	while not res_dict:
		count+=1
		logsup.logger.info(f'Starting "{func.__name__}". Counter: {count}')
		p=mp.Process(target=func,args=args,kwargs=kwargs)
		p.start()
		p.join(retry_timeout)
		p.terminate()
	return res_dict

def run_processes_with_map_async(proc_func,payload: list,proc_count=None):
	proc_count=proc_count or (mp.cpu_count()-1)
	with mp.Pool(proc_count) as p:
		results=list()
		p.map_async(proc_func,payload,callback=lambda x:results.extend(x))
		p.close()
		p.join()
	return results

def run_reactive_worker(listening_func,job_func,output_func=None,worker_count=1,interval=10):
	with concurrent.futures.ProcessPoolExecutor(worker_count) as executor:
		rx.Observable.interval(interval).from_iterable(listening_func()).flat_map(
			lambda *args,**kwargs:executor.submit(job_func,*args,**kwargs)
			).subscribe(output_func)

class ReactiveTask(ABC):
	
	def __init__(self,filename,interval=10):
		self.filename=filename
		self.interval=interval
	
	def sleep(self):
		time.sleep(self.interval)
	
	def create_log_file(self,info_opts=None,**kwargs):
		logsup.logger.create_log_file(self.filename,dict(process=self.__class__.__name__,**(info_opts or {})),**kwargs)
	
	def data_generator(self):
		raise NotImplementedError
	
	def data_processor(self,data):
		raise NotImplementedError
	
	def post_processor(self,output_data):
		pass
	
	def run(self,worker_count=1):
		with concurrent.futures.ThreadPoolExecutor(worker_count) as executor:
			# timing_observable=rx.Observable.interval(int(self.interval*1e3))
			# timing_observable.from_(self.data_generator()).flat_map(lambda data:executor.submit(run_processes_with_map_async,self.data_processor,payload=[data],proc_count=1))\
			# 	.subscribe(self.post_processor)
			rx.Observable.from_iterable(iter(self.data_generator()))\
				.flat_map(lambda data:executor.submit(
				run_processes_with_map_async,self.data_processor,payload=[data],proc_count=1))\
				.subscribe(self.post_processor)
			# rx.Observable\
			# 	.zip(timing_observable,processor_observable,lambda t,output_data:output_data)\
			# 	.flat_map(lambda data:executor.submit(run_processes_with_map_async,self.data_processor,payload=[data],proc_count=1))\
			# 	.subscribe(self.post_processor)
			input('The run finished. Give any input: ')

class ConveyorPosition:
	
	def __init__(self,job_func,max_process_count=1):
		self.job_func=job_func
		self.max_process_count=max_process_count
		self.current_process_count=0
		self.processes=list()
	
	def check_for_completed_processes(self):
		for p in self.processes:
			if not p.is_alive():
				p.join()
				p.terminate()
				self.processes.remove(p)
				self.current_process_count-=1
	
	def start_process(self,target,*args,name=None,**kwargs):
		if self.current_process_count<self.max_process_count:
			# simple_logger.info('Starting process...')
			p=mp.Process(target=target,args=args,kwargs=kwargs,name=name)
			p.start()
			self.processes.append(p)
			self.current_process_count+=1

def queue_generator(queue: mp.Queue,func,control_desk,output=None):
	if output is None:
		resultant_status,data=func()
	else:
		resultant_status,data=output
	for i,row in control_desk.iterrows():
		if func==row.gen_func:
			if resultant_status==row.ret_stat or (type(row.ret_stat) is types.FunctionType and row.ret_stat(resultant_status)):
				logsup.logger.info('resultant_status: %s,data: %s',resultant_status,data)
				queue.put((row.name,data))

def queue_processor(queue: mp.Queue,control_desk):
	# simple_logger.info('control_desk: %s',control_desk)
	row_name,data=queue.get()
	logsup.logger.pop()
	try:
		func=control_desk.loc[row_name].doer_func
		output=func(data)
		if output is None: return
		queue_generator(queue,func,control_desk,output)
	
	except Exception as e:
		logsup.logger.error(str(e),exc_info=True)
		logsup.logger.inform(str(e),exc_info=True)
		ScheduledTask.on_process_error(data,e)
		raise
	pass

class Conveyor:
	
	def __init__(self,max_queue_size=1,name=''):
		self.control_desk=pd.DataFrame(columns=['gen_func','ret_stat','doer_func'])
		self.queue=mp.Queue()
		self.max_q_size=max_queue_size
		self.positions: List[ConveyorPosition]=list()
		self.funcs_to_run_at_start=set()
		self.has_doer=False
		self.name=name or uuid.uuid4()
	
	def add_control_row(self,*args):
		self.control_desk.loc[self.control_desk.shape[0]]=args
	
	def add_data_provider(self,scheduled_job: schedule.Job,func,run_at_start=True):
		if run_at_start: self.funcs_to_run_at_start.add(func)
		self.add_control_row(func,True,None)
		scheduled_job.do(queue_generator,self.queue,func,self.control_desk).tag(self.name)
		return self
	
	def add_return_status_info(self,some_func,returns_status=True):
		for i,row in self.control_desk.iterrows():
			if some_func==row.gen_func:
				if row.ret_stat is True:
					row.ret_stat=returns_status
					return
		self.add_control_row(some_func,returns_status,None)
	
	def add_doer_func(self,doer_func,max_workers=1):
		# self.control_desk.loc[self.control_desk['doer_func'].isnull() & (self.control_desk['ret_stat'].notnull()),'doer_func']=doer_func
		check1=(self.control_desk['doer_func'].isnull()&self.control_desk['ret_stat'].notnull())
		if check1.any():
			self.control_desk.loc[check1,'doer_func']=doer_func
		else:
			self.control_desk.loc[self.control_desk['doer_func'].isnull()&
			                      (self.control_desk['ret_stat'].isnull()),
			                      ['ret_stat','doer_func']]=True,doer_func
		# print(self.control_desk)
		# raise NotImplementedError
		# for i,row in self.control_desk.iterrows():
		# 	if row.ret_stat is None:
		# 		self.add_return_status_info(row.gen_func)
		# if row.doer_func is None:
		# 	if row.ret_stat is not None:
		# 		row.doer_func=doer_func
		
		#
		# if self.has_doer:
		# 	if row.doer_func is None and row.ret_stat is None:
		# 		row.doer_func=doer_func
		# 		row.ret_stat=True
		# else:
		# 	if row.doer_func is None and row.ret_stat is not None:
		# 		row.doer_func=doer_func
		self.__add_position(doer_func,max_workers=max_workers)
		self.has_doer=True
	
	def __add_position(self,worker_func,max_workers=1):
		conv_position=ConveyorPosition(job_func=worker_func,max_process_count=max_workers)
		self.positions.append(conv_position)
	
	def run_start_funcs(self):
		for func in self.funcs_to_run_at_start:
			queue_generator(self.queue,func,self.control_desk)
	
	def run_pending(self):
		# simple_logger.info('conveyor: %s, qsize: %s',self.name,self.queue.qsize())
		for conv_pos in self.positions:
			conv_pos.check_for_completed_processes()
			conv_pos.start_process(queue_processor,self.queue,self.control_desk)
		if self.queue.qsize()<self.max_q_size:
			schedule.run_pending(self.name)
		pass

class ScheduledTask:
	
	def __init__(self,parent_task=None,filename=None,log_opts=None,**setup_kwargs):
		if parent_task is not None: parent_task.child_tasks.append(self)
		self.parent_task=parent_task
		self.child_tasks=list()
		self.filename=filename
		if not self.filename is None: self.create_log_file(level=logsup.INFORM,**(log_opts or {}))
		else: self.filename=self.parent_task.filename
		self.conveyors: List[Conveyor]=list()
		self.current_conveyor: Conveyor=None
		self.setup(**setup_kwargs)
	
	def setup(self,**kwargs):
		pass
	
	def create_log_file(self,**kwargs):
		assert self.filename is not None
		logsup.logger.create_log_file(self.filename,process=self.__class__.__name__,**kwargs)
	
	def check_for(self,func,scheduler,check_at_start=True,**kwargs):
		if self.current_conveyor is None or self.current_conveyor.has_doer:
			c=Conveyor(**dict(dict(name=f"Conveyor-{len(self.conveyors)}"),**kwargs))
			self.conveyors.append(c)
			self.current_conveyor=c
		# self.checker_functions.append(func)
		# self.checker_functions[q]=func
		# self.conveyor_queues[self.current_conveyor].append(q)
		self.current_conveyor.add_data_provider(scheduled_job=scheduler,func=func,run_at_start=check_at_start)
		return self
	
	def when(self,some_func=None,return_status=True):
		if some_func is None: some_funcs=self.current_conveyor.control_desk['gen_func'].tolist()
		else: some_funcs=[some_func]
		if self.current_conveyor.has_doer:
			for some_func in some_funcs:
				self.current_conveyor.add_control_row(some_func,return_status,None)
		else:
			for func in some_funcs:
				# assert func in gen_funcs,"The function should be in the current conveyor's list of generator functions"
				self.current_conveyor.add_return_status_info(some_func=func,returns_status=return_status)
		return self
	
	def do(self,func,workers_count=1):
		self.current_conveyor.add_doer_func(func,max_workers=workers_count)
		self.current_conveyor.add_control_row(func,None,None)
		return self
	
	def run(self,*tasks,sleep_time=1):
		all_tasks=[self,*tasks,*self.child_tasks]
		for task in all_tasks:
			for conveyor in task.conveyors: conveyor.run_start_funcs()
		logsup.logger.info('Start of the main loop.')
		while True:
			for task in all_tasks:
				for conveyor in task.conveyors:
					conveyor.run_pending()
			time.sleep(sleep_time)
	
	@staticmethod
	def on_process_error(data,exception):
		logsup.logger.exception("Exception caught when processing data:\n%s\nException text:\n%s",data,str(exception))

def infiterate(iter_obj,max_iter_count=None,next_getter=None,inform_count=8):
	if isinstance(iter_obj,int):
		an_iterable,iter_count=range(iter_obj),iter_obj
	else:
		an_iterable=iter_obj
		if isinstance(iter_obj,Sized):
			iter_count=len(iter_obj)
		else:
			assert max_iter_count
			iter_count=max_iter_count
	max_iter_count=max_iter_count or iter_count
	if next_getter is None: next_getter=lambda obj:obj
	for i,obj in enumerate(an_iterable):
		if i%(max_iter_count//inform_count)==0: logsup.logger.info('%d%%, i=%d',i/(max_iter_count-1)*100,i)
		
		obj=next_getter(obj)
		yield obj
		if i==max_iter_count-1:
			logsup.logger.info('%d%%, i=%d',i/(max_iter_count-1)*100,i)
			return

class ParallelTasker:
	
	def __init__(self,func,*args,**kwargs):
		self.partial_func=partial(func,*args,**kwargs)
		self.queue=mp.Queue()
		self._total_proc_count=0
		pass
	
	def set_run_params(self,**kwargs):
		val_lengths={len(v) for v in kwargs.values()}
		assert len(val_lengths)==1
		val_length=val_lengths.pop()
		
		for i in range(val_length):
			self.queue.put((i,{k:v[i] for k,v in kwargs.items()}))
			self._total_proc_count+=1
			logsup.logger.info('self._total_proc_count: %s',self._total_proc_count)
		
		return self
	
	def __process_func(self,queue,common_list):
		i,kwargs=queue.get()
		result=self.partial_func(**kwargs)
		common_list.append([i,result])
	
	@staticmethod
	def __join_finished_processes(active_procs,sleep_time):
		while True:
			# simple_logger.info('Process queue is full. Searching for finished processes.')
			for p in active_procs:
				if not p.is_alive():
					logsup.logger.info('Finished process found. Joining it.')
					active_procs.remove(p)
					p.join()
					# p.terminate()
					logsup.logger.info('Process successfully removed.')
					return
			time.sleep(sleep_time)
	
	def run(self,workers_count=None,sleep_time=1.0):
		workers_count=min(mp.cpu_count()-1,workers_count or self._total_proc_count)
		manager=mp.Manager()
		common_list=manager.list()
		processes=[mp.Process(target=self.__process_func,args=(self.queue,common_list)) for _ in range(self.queue.qsize())]
		active_procs=list()
		while True:
			logsup.logger.info('loop begins')
			if len(processes)==0:
				logsup.logger.info('Waiting for the last jobs to finish.')
				for active_p in active_procs:
					active_p.join()
				break
			if len(active_procs)<workers_count:
				logsup.logger.info('Adding a process')
				proc=processes.pop()
				proc.start()
				active_procs.append(proc)
			else:
				self.__join_finished_processes(active_procs,sleep_time)
			time.sleep(sleep_time)
		return [item[1] for item in sorted(common_list,key=lambda x:x[0])]

def try_wrapper(max_tries=12,max_sleep_time=600,pass_error=True,on_pass_return=None):
	# if pass_error: assert on_pass_return is not None
	if max_tries in [None,'inf']: max_tries=float('inf')
	
	def decorator(func):
		def wrapper(*args,**kwargs):
			try_count=1
			while True:
				try:
					out=func(*args,**kwargs)
					if try_count!=1:
						logsup.logger.info('Succeeded at try #%d',try_count)
					break
				except Exception as e:
					if max_tries and max_tries<=try_count:
						logsup.logger.info('Reached max. number of tries (%d).',try_count)
						if pass_error: return on_pass_return
						else: raise
					try_count+=1
					if max_tries==float('inf'): sleep_time=max_sleep_time
					else: sleep_time=max_sleep_time/(1+np.exp(-(try_count-1-max_tries/2)))
					
					logsup.logger.error('error: %s',str(e),exc_info=True)
					logsup.logger.info('Sleeping for %.3f seconds.',sleep_time)
					time.sleep(sleep_time)
					logsup.logger.info('Try #%d',try_count)
			
			return out
		
		return wrapper
	
	return decorator

_try_wrapper_attrs="_obj _try_wrapper_args _try_wrapper_kwargs".split(' ')

class TryWrapper:
	
	def __init__(self,obj,*try_wrapper_args,**try_wrapper_kwargs):
		self._obj=obj
		self._try_wrapper_args=try_wrapper_args
		self._try_wrapper_kwargs=try_wrapper_kwargs
	
	def _func_wrapper(self,func):
		return func
	
	def __getattr__(self,item):
		if item in _try_wrapper_attrs: return self.__dict__[item]
		else:
			attr=getattr(self._obj,item)
			if type(attr) is types.MethodType:
				return try_wrapper(*self._try_wrapper_args,**self._try_wrapper_kwargs)(self._func_wrapper(attr))
			else: return attr

class GenericObjContainer:
	
	def __init__(self,obj):
		self.obj=obj

class ReactiveObj(GenericObjContainer):
	
	def apply(self,func):
		if isinstance(self.obj,Iterable):
			return list(map(func,self.obj))
		else: return func(self.obj)

class Mapper(GenericObjContainer):
	
	def map(self,func):
		return list(map(func,self.obj))

class AttributeItemGetterSetter:
	
	def __init__(self,obj):
		self.obj=obj
	
	def __getattr__(self,item):
		return AttributeItemGetterSetter(self.obj[item])
	
	def __getitem__(self,item):
		return AttributeItemGetterSetter(self.obj[item])
	
	def __setitem__(self,key,value):
		self.obj[key]=value
	
	def __repr__(self):
		return f"AttributeItemGetterSetter({pformat(self.obj)})"
	
	def __call__(self,*args,**kwargs):
		return self.obj

class AttributeItemSetter:
	
	def __init__(self,obj):
		self.obj=obj
	
	def __setattr__(self,key,value):
		self.obj[key]=value
	
	def __setitem__(self,key,value):
		self.obj[key]=value
	
	def __repr__(self):
		return f"AttributeItemSetter({pformat(self.obj)})"

class ConfigReader(AttributeItemGetterSetter):
	
	def __init__(self,config_path):
		self.config_path=config_path
		self.yaml=raml.YAML()
		self.yaml.default_flow_style=False
		super(ConfigReader,self).__init__(self.__load())
	
	def __load(self):
		return self.yaml.load(open(self.config_path))
	
	def update(self):
		self.yaml.dump(self.obj,open(self.config_path,'w'))
		return self.__load()

if __name__=='__main__':
	pass

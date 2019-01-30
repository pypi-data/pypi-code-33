#!usr/bin/env python
#-*- coding:utf-8 -*-
import os
import time
import inspect
import signal
import ctypes
import traceback
from gevent import sleep
from threading import Thread
from multiprocessing import Process, Queue
from gevent.event import AsyncResult

from .libs.util import make_hash

def _async_raise(tid, exctype):
    """raises the exception, performs cleanup if needed"""
    tid = ctypes.c_long(tid)
    if not inspect.isclass(exctype):
        exctype = type(exctype)
    res = ctypes.pythonapi.PyThreadState_SetAsyncExc(
        tid, ctypes.py_object(exctype))
    if res == 0:
        raise ValueError("invalid thread id")
    elif res != 1:
        # """if it returns a number greater than one, you're in trouble,
        # and you should call it again with exc=NULL to revert the effect"""
        ctypes.pythonapi.PyThreadState_SetAsyncExc(tid, None)
        raise SystemError("PyThreadState_SetAsyncExc failed")


def _stop_thread(thread):
    _async_raise(thread.ident, SystemExit)


# 5 Task Status
PENDING = 'PENDING'
RUNNING = 'RUNNING'
SUCCESS = 'SUCCESS'
FAILURE = 'FAILURE'
CANCELED = 'CANCELED'

# TASK RUN METHOD
WITH_GEVENT = 0
WITH_THREAD = 1
WITH_PROCESS = 2
DEFAULT_METHOD = WITH_PROCESS

class Plugin(object):
    def __init__(self, logger, up_queue, task_id, **param):
        self.param = param
        self.up_data_queue = up_queue
        self.logger = logger
        self.op_queue = Queue()
        self.error_queue = Queue()
        self.task_id = task_id
        self.task_status = PENDING
        self._p_start_time = time.time()
        self._p_end_time = 0
        self.running_ins = None

        self.is_del = False

    def __del__(self):
        if self.is_del: return
        self.is_del = True
        self._p_end_time = time.time()

        status = self.get_task_status()

        if self.task_status == RUNNING:
            self.task_status = SUCCESS
            status['RUNNING_STATUS'] = self.task_status

        self.up_data_queue.put(status)

        self.logger.info('PLUGIN: %s , STATUS: %s' % (
            status['PLUGIN_NAME'], status['RUNNING_STATUS']))


    def start(self, method=DEFAULT_METHOD):
        if method == WITH_THREAD:
            self.start_thread()
        else:
            self.start_process()


    def start_thread(self):
        self.running_ins = Thread(target=self.run, kwargs=self.param)
        self.running_ins.daemon = True
        self.running_ins.start()

        self.task_status = RUNNING
        self.logger.info('start_thread ins-id : %s ' % (self.running_ins))

        # PUSH TASK STATUS
        status = self.get_task_status()
        self.up_data_queue.put(status)

    def start_process(self):
        self.running_ins = Process(target=self.run, kwargs=self.param)
        self.running_ins.daemon = True
        self.running_ins.start()
        self.logger.info('start_process ins-id : %s ' % (self.running_ins))
        self.task_status = RUNNING

        # PUSH TASK STATUS
        status = self.get_task_status()
        self.up_data_queue.put(status)

    def stop_task(self):
        self.task_status = 'CANCELED'

        if isinstance(self.running_ins, Thread):
            return _stop_thread(self.running_ins)

        elif isinstance(self.running_ins, Process):
            os.kill(self.running_ins.pid, signal.SIGKILL)

    def restart_task(self):
        opid = self.running_ins.pid
        self.start_process()

        os.kill(opid, signal.SIGKILL)

    def run(self, **param):
        '''
        Call the plugin
        '''
        try:

            self.operate(**param)
        except Exception as e:
            err = traceback.format_exc()
            self.logger.error(err)
            self.error_queue.put(err)

    def push(self, _data):
        '''
        push task result
        '''
        data = {'data': _data}
        data['PLUGIN_NAME'] = self.__class__.__name__
        data['MSG_TYPE'] = 'TASK_DATA'
        data['AGENT_ID'] = __sumeru__.AGENT_ID
        data['TASK_ID'] = self.task_id
        data['UNIX_TIME'] = time.time()
        data['START'] = self._p_start_time
        data['END'] = time.time()
        self.up_data_queue.put(data)
        return data

    def operate(self, **param):
        pass

    def get_task_status(self):
        err = ""
        if self.error_queue.qsize():
            self.task_status = FAILURE
            try:
                err = self.error_queue.get_nowait()
            except Exception as e:
                err = ''
    
        return {'AGENT_ID': __sumeru__.AGENT_ID,
                'TASK_ID': self.task_id,
                'MSG_TYPE': 'TASK_STATUS',
                'RUNNING_STATUS': self.task_status,
                'LAST_START_TIME': self._p_start_time,
                'LAST_FINISH_TIME': self._p_end_time,
                'ERROR': err,
                'DATA': [],
                'PLUGIN_NAME': self.__class__.__name__}

    def check_status(self):
        _running = None
        if self.running_ins != None:
            if isinstance(self.running_ins, Process):
                if not self.running_ins.is_alive():
                    _running = SUCCESS

            elif isinstance(self.running_ins, Thread):
                if not self.running_ins.isAlive():
                    _running = SUCCESS
            else:
                _running = CANCELED

            return _running

        

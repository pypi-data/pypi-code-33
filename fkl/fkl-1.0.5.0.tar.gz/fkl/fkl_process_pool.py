# -*- coding: utf-8 -*-
import multiprocessing
from multiprocessing import Process
from multiprocessing.queues import SimpleQueue
from threading import Thread
import time
class FKLProcessPool:
    def __init__(self,process_num):
        self._funtion_queue=multiprocessing.Manager().Queue()
        self._result_queue=multiprocessing.Manager().Queue()
        self._result_dict={}
        self._process_queue=[multiprocessing.Manager().Queue() for i in range(process_num)]
        self._process=[Process(target=self._Process,args=(i,self._process_queue[i],self._funtion_queue,self._result_queue)) for i in range(process_num)]
        self._process_num=process_num
        self._result_thread=Thread(target=self._ResultThread)
        self._result_thread_switch=True
        self._execute_count=0
    def _Process(self,process_number,process_queue,function_queue,result_queue):
        this_process_number=process_number
        this_process_queue=process_queue
        while(this_process_queue.empty()==True):
            if(function_queue.empty()==False):
                execute_mark,function,parameter=function_queue.get()
                if(parameter==None):result=function()
                else:result=function(parameter)
                result_queue.put([execute_mark,result])
            time.sleep(0.1)
        this_process_queue.get()
        return
    def _ResultThread(self):
        while(self._result_thread_switch==True):
            if(self._result_queue.empty()==False):
                execute_mark,result=self._result_queue.get()
                self._result_dict[execute_mark]=result
            time.sleep(0.1)
        return
    def __call__(self,function,parameter=None):
        return self.Push(function,parameter)
    def __getitem__(self,execute_mark):
        return self.GetResult(execute_mark)
    def Push(self,function,parameter=None):
        execute_mark=self._execute_count
        self._funtion_queue.put([execute_mark,function,parameter])
        self._execute_count+=1
        return execute_mark
    def GetResult(self,execute_mark,block=True,time_gap=0.1):
        if(block==True):
            while(1):
                result=self._result_dict.get(execute_mark,False)
                if(result!=False):break
                time.sleep(time_gap)
        else:
            result=self._result_dict.get(execute_mark,False)
        if(result!=False):del self._result_dict[execute_mark]
        return result
    def Start(self):
        for i in range(self._process_num):
            self._process[i].start()
        self._result_thread_switch=True
        self._result_thread.start()
        return
    def Stop(self):
        for i in range(self._process_num):
            self._process_queue[i].put(0)
        self._result_thread_switch=False
        return 

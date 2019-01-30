#! /usr/bin/env python
#coding=utf-8
from __future__ import print_function, division, absolute_import
import os
import time
import socket
import psutil
import platform


def get_ip():
    '''
    获取IP
    '''
    return [(s.connect(('8.8.8.8', 80)), s.getsockname()[0], s.close())
        for s in [socket.socket(socket.AF_INET, socket.SOCK_DGRAM)]][0][1]

def load_stat():
    '''
    get system load  stat
    '''
    # TODO  Windows Platform Compatibility
    loadavg = {}
    f = open("/proc/loadavg")
    con = f.read().split()
    f.close()
    loadavg['lavg_1'] = con[0]
    loadavg['lavg_5'] = con[1]
    loadavg['lavg_15'] = con[2]
    loadavg['nr'] = con[3]
    loadavg['last_pid'] = con[4]
    return loadavg

def get_sys_info():
    '''
    Get the System information
    '''
    cpu_usage = psutil.cpu_percent(interval=0.1, percpu=False)
    cpu_count = psutil.cpu_count(logical=True)
    memory = psutil.virtual_memory()
    DIR = '/'
    default_eth = psutil.net_io_counters()

    sys_info = {
                'CPU_USAGE': cpu_usage,
                'LOGICAL_CPU_CORE_NUM': cpu_count,
                'RAM_USAGE': memory.percent,
                'LOAD_AVG': load_stat()['lavg_15'],
                'TOTAL_MEM':memory.total/(1024**3),
                'USED_MEM':float(memory.total - memory.available)/(1024**3),
                'DISK_USAGE':psutil.disk_usage(DIR).percent,
                'TOTAL_DISK':psutil.disk_usage(DIR).total/(1024**3),
                'USED_DISK':psutil.disk_usage(DIR).used/(1024**3),
                'NETWORK_SEND':float(default_eth.bytes_sent)/(1024**3),
                'NETWORK_RECV':float(default_eth.bytes_recv)/(1024**3),
                'BOOT_TIME':psutil.boot_time(),
                'OS': '{} ({})'.format(platform.uname()[0], platform.uname()[-1]),
                'RUN_COST': time.time()-psutil.Process(os.getpid()).create_time()
                }
    return sys_info
 

#!usr/bin/env python
#-*- coding:utf-8 -*-

import os
import sys
import ast
import time
import copy
import json
import traceback
import threading

from .plugin import Plugin
from .libs.util import load_json, pip_install, pip_check, import_check
from sumeru.manage.libs.util import get_plugins
import multiprocessing


class PluginManager(object):
    WITH_GEVENT = 0
    WITH_THREAD = 1
    WITH_PROCESS = 2
    DEFAULT_METHOD = WITH_PROCESS

    def __init__(self, data_queue, task_queue, running_tasks, logger):
        '''
            plugin manager
        '''
        self.__logger = logger
        self.plugin_list = {}
        self.plugin_md5 = []
        self.current_task_list = {}
        self.data_queue = data_queue
        self.task_queue = task_queue
        self.running_tasks = running_tasks
        self._load_plugins()

    def _load_plugins(self):
        plugins = get_plugins()
        if plugins == self.plugin_md5:
            return
        else:
            self.plugin_md5 = []
            self.plugin_list = {}

        plugin_path = os.sep.join([__sumeru__.PLUGIN_PATH, 'plugins'])
        if not os.path.exists(plugin_path):
            self.__logger.warning('Plugin Dir Not Exist')
            return []

        if not sys.path.count(plugin_path):
            sys.path.append(plugin_path)

        for plugin_dir in os.listdir(plugin_path):
            p = os.sep.join([__sumeru__.PLUGIN_PATH, 'plugins', plugin_dir])
            if not os.path.isdir(p): continue

            f_config = os.sep.join([p, 'config.json'])
            if not os.path.exists(f_config): continue

            self.plugin_md5.append(plugin_dir)

            config = load_json(f_config)
            plugin_name = config.get('plugin_name')
            py_deps = config.get('py_deps', [])
            sys_deps = config.get('sys_deps', [])
            for opt, deps in sys_deps.items():
                for dep in deps:
                    try:
                        import commands
                        commands.getstatusoutput("{} install {} -y".format(opt, dep))
                    except Exception as e:
                        pass

            for dep_py_package in py_deps:
                if not (pip_check(dep_py_package) | import_check(dep_py_package)):
                    pip_install(dep_py_package)
            try:
                plugin = __import__('{}.{}'.format(plugin_dir, plugin_name), fromlist=[plugin_name])
                self.plugin_list.update({plugin_name: plugin})
            except Exception as e:
                self.__logger.error(traceback.format_exc() + '|plugin_name:' + plugin_name)

        self.__logger.info('Available Plugins --:' + str(self.plugin_list.keys()))
        return self.plugin_list.keys()


    def start_tasks(self, new_tasks):
        for task_id, new_task in new_tasks.items():

            if task_id in self.current_task_list.keys():
                OP = new_task.get('OP')
                if OP == 'STOP':
                    self.current_task_list[task_id]['INSTANCE'].stop_task()
                elif OP == 'RESTART':
                    self.current_task_list[task_id]['INSTANCE'].restart_task()

                if self.current_task_list[task_id].get('OP'):
                    self.current_task_list[task_id]['INSTANCE'].op_queue.put(
                        self.current_task_list[task_id]['OP'])

            else:
                plugin_name = new_task.get('PLUGIN_NAME')
                run_method = new_task.get('RUN_METHOD')
                if plugin_name in self.plugin_list.keys():
                    self.current_task_list[task_id] = dict(TASK_ID = task_id, PLUGIN_NAME = new_task['PLUGIN_NAME'])

                    ins = getattr(self.plugin_list[plugin_name], plugin_name)
                    obj = ins(self.__logger, self.data_queue, task_id, **new_task['PARAM'])
                    self.current_task_list[task_id]['INSTANCE'] = obj

                    obj.start(method=run_method)
                else:
                    self.__logger.error('Unknown Plugin Name : %s' % (plugin_name))
                    self.data_queue.put(self.get_status(plugin_name, task_id, 'FAILURE', 'Unknown Plugin Name {}'.format(plugin_name)))
                    continue


    def get_status(self, plugin_name, task_id, task_status, err):
        return {'AGENT_ID': __sumeru__.AGENT_ID,
                'TASK_ID': task_id,
                'MSG_TYPE': 'TASK_STATUS',
                'RUNNING_STATUS': task_status,
                'LAST_START_TIME': 0,
                'LAST_FINISH_TIME': 0,
                'ERROR': err,
                'DATA': [],
                'PLUGIN_NAME': plugin_name}

    def get_running_tasks(self):
        result = {}
        for task_id in list(self.current_task_list.keys()):
            task = self.current_task_list[task_id]
            ins = task.get('INSTANCE')
            if not ins: continue
            task_status = ins.check_status()

            if task_status not in ['SUCCESS', 'FAILURE', 'CANCELED']:
                result[task_id] = {'TASK_ID': task_id, 'PLUGIN_NAME': task['PLUGIN_NAME']}

        return result

    def task_loop(self):
        for task_id in list(self.current_task_list.keys()):
            task = self.current_task_list[task_id]
            ins = task.get('INSTANCE')
            if not ins:
                self.current_task_list.pop(task_id)
                continue

            if ins.check_status() in ['SUCCESS', 'FAILURE', 'CANCELED']:
                self.current_task_list.pop(task_id)
                ins.__del__()

        new_tasks = self.get_task_list_from_queue()
        if new_tasks:
            self.start_tasks(new_tasks)

    def get_task_list_from_queue(self):
        task_list = {}

        while not self.task_queue.empty():
            task_data = self.task_queue.get()
            task = json.loads(task_data)
            task_list.update({task["TASK_ID"]: task})
        return task_list


    def check_plugin_status_loop(self):
        while True:
            try:
                time.sleep(1)
                self._load_plugins()
                self.task_loop()
                running_tasks = self.get_running_tasks()
                if running_tasks:
                    self.running_tasks.put(running_tasks)

            except Exception as e:
                self.__logger.error(traceback.format_exc())

    def manager_start(self):
        engine_thread = multiprocessing.Process(target=self.check_plugin_status_loop)
        engine_thread.start()
        return engine_thread


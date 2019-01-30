#!encoding=utf-8
from __future__ import print_function, division, absolute_import
import os
import sys
import time
import json
import base64
import hashlib
import logging
import traceback
import collections
from hashlib import md5
from datetime import datetime

import zipfile
import tornado.web
import pymysql
from playhouse.db_url import connect
from playhouse.shortcuts import model_to_dict

from sumeru import versions
from .libs.util import *
from .libs.models import *
from .libs.sysinfo import get_sys_info, get_ip
from .libs.crython_api import (enable_cron_job,unable_cron_job, run_cron_job,
                              stop_job)
from sumeru.manage.conf import set_conf, set_scheduler

logger = logging.getLogger('sumeru.scheduler')

STATUS_COLOR = {
            "PENDING": { 
                    "borderColor": '#DD22DD',
                    "color":"#DD22DD",
            },
            "RUNNING": { 
                    "borderColor": '#19b1dabf',
                    "color":"#19b1dabf",
            },
            "SUCCESS": { 
                    "borderColor": '#33CC8F',
                    "color":"#33CC8F",
            },
            "FAILURE": { 
                    "borderColor": '#FF0033',
                    "color":"#FF0033",
            },
            "CANCELED": { 
                    "borderColor": '#808080',
                    "color":"#808080",
            }
        }

def password_md5(o):
    return md5('{}.{}'.format(md5(md5(o.encode()).hexdigest().encode()).hexdigest(), "fo87u23i47rfyhj").encode()).hexdigest()


"""
__sumeru__.db.table_exists("user")
"""


class LoginedRequestHandler(tornado.web.RequestHandler):
    uid = property(lambda self: self.get_secure_cookie("__SUMERU__"))

    def prepare(self):
        if self.request.uri.startswith("/api/login") and self.request.method == 'GET':
            return

        if self.request.uri in ["/api/is_install", "/api/install"]:
            return

        if __sumeru__.db.is_closed():
            __sumeru__.db.connect()

        if self.request.uri.startswith("/api/login"):
            return

        if not self.uid:
            self.redirect('/#/login')
            self.send_error(403)

    def on_finish(self):
        if not __sumeru__.db.is_closed():
            __sumeru__.db.close()

    def send_error(self, status_code, **kwargs):
        error_trace_list = traceback.format_exception(*kwargs.get("exc_info"))
        self.write(dict(status = False, status_code = status_code, msg = error_trace_list))
        self.finish()

    async def refresh_layout(self, _id, layout):
        nodes = {}
        for item in layout['node_list']:
            node_key = "layout_{}_{}".format(_id, item["_id"])
            nodes[node_key] = {"node_id": node_key, "child": [], "name": item["plugin_type"], "parent": []} 

        for item in layout['connection_list']:
            node_source_id = "layout_{}_{}".format(_id, item["node_source_id"])
            node_target_id = "layout_{}_{}".format(_id, item["node_target_id"])
            nodes[node_source_id]['child'].append(node_target_id)
            nodes[node_target_id]['parent'].append(node_source_id)

        for k, v in nodes.items():
            if not v['parent']:
                await __sumeru__.scheduler.HA.write("/layout_id/{}".format(_id), k)

            await __sumeru__.scheduler.HA.write("/component_id/{}".format(k), json.dumps(v))


    async def get_tasks(self, task_id, r = []):
        task = await __sumeru__.scheduler.HA.read('/task_id/{}'.format(task_id))
        if not task: return
        task = json.loads(task.value)
        component_id = task['component_id']
        component = await __sumeru__.scheduler.HA.read("/component_id/{}".format(component_id))
        component = json.loads(component.value)
        task['component_name'] = component['name']
        r.append(task)
        childs = task['child']
        for child in childs:
            await self.get_tasks(child, r = r)

    async def tree_tasks(self, task_id):
        task = await __sumeru__.scheduler.HA.read('/task_id/{}'.format(task_id))
        if not task: return

        task = json.loads(task.value)
        component_id = task['component_id']
        component = await __sumeru__.scheduler.HA.read("/component_id/{}".format(component_id))
        component = json.loads(component.value)

        _task = {}

        name = "ROOT" if task['parent'] == 0 else component['name']
        _task['name'] = "ROOT" if task['parent'] == 0 else ''
        _task['result'] = {'params': json.dumps(task['params']), 'status': task.get('status'), 'name': name}
        agent = DNode.get_or_none(DNode.node_id == task.get('agent_id'))
        if agent:
            _task['result']['agent_name'] = agent.node_name
            _task['result']['agent_addr'] = agent.node_addr

        _task['value'] = 1
        _task['symbol'] = 'circle'
        _task['itemStyle'] = STATUS_COLOR.get(task.get('status'), {})

        childs = task['child']
        children = []
        for child in childs:
            c_task = await self.tree_tasks(child)
            children.append(c_task)

        _task['children'] = children
        return _task


class LoginHandler(LoginedRequestHandler):
    def get(self):
        self.write(dict(status = True))

    def post(self):
        username = self.get_argument('username')
        password = password_md5(self.get_argument('password'))

        user = User.get_or_none(User.username == username and \
                                User.password == password)

        if not user:
            self.write(dict(status = False, msg = "USERNAME OR PASSWORD FAILURE"))
        elif not user.enable:
            self.write(dict(status = False, msg = "USER DISABLE"))
        else:
            self.set_secure_cookie("__SUMERU__", str(user.id))
            self.write(dict(status = True, msg = "SUCCESS"))

class LogoutHandler(tornado.web.RequestHandler):
    def get(self):
        self.clear_cookie("__SUMERU__")
        self.write(dict(status = True, msg = "SUCCESS"))

class DashBoardHandler(LoginedRequestHandler):
    def get(self):
        info = get_sys_info()
        info['IP'] = get_ip()
        info['VERSION'] = versions.get_versions()
        info['TASK_COUNT'] = TaskIns.select().count()
        info['TASK_RUNNING_COUNT'] = TaskIns.select().where(TaskIns.running_status.in_(['RUNNING', 'PENDING'])).count()
        info['TASK_SUCCESS_COUNT'] = TaskIns.select().where(TaskIns.running_status == 'SUCCESS').count()
        info['TASK_FAIL_COUNT'] = TaskIns.select().where(TaskIns.running_status == 'FAILURE').count()
        info['CRONTASK_COUNT'] = CronTask.select().where(CronTask.task_type == 1).count()
        info['DNODE_COUNT'] = DNode.select().count()
        info['UPLINK_SPEED'] = __sumeru__.scheduler.uplink_speed
        info['DOWNLINK_SPEED'] = __sumeru__.scheduler.downlink_speed
        info['UNIX_TIME'] = time.time()
        info['CURRENT_TASK_COUNT'] = int(__sumeru__.scheduler.mq.get('task_count'))
        info['MAX_TASK_COUNT'] = int(__sumeru__.scheduler.mq.get('max_task_count'))
        info['TPS_CURRENT_TASK_COUNT'] = int(__sumeru__.scheduler.mq.get('tps_current_task_count') or 0)
        info['TPS_MAX_TASK_COUNT'] = int(__sumeru__.scheduler.mq.get('tps_max_task_count') or 0)

        self.write(dict(status = True, result = info))

class GroupAddHandler(LoginedRequestHandler):
    def post(self):
        group_name = self.get_argument('group_name')
        ret = Group(group_name = group_name).save()
        if ret:
            self.write(dict(status = 1, msg = 'SUCCESS'))
        else:
            self.write(dict(status = 0, msg = 'FAILURE'))

class GroupDelHandler(LoginedRequestHandler):
    def post(self):
        _ids = self.get_arguments('id')
        ret = Group.delete().where(Group.id.in_(_ids)).execute()
        DNodeGroup.delete().where(DNodeGroup.group_id.in_(_ids)).execute()
        if ret:
            self.write(dict(status = 1, msg = 'SUCCESS'))
        else:
            self.write(dict(status = 0, msg = 'FAILURE'))

class GroupListHandler(LoginedRequestHandler):
    def get(self):
        search = self.get_argument('search', None)
        status = self.get_argument('status', None)
        page_index = int(self.get_argument('page_index', 1))
        page_size = int(self.get_argument('page_size', 10))

        if search and status:
            cond = ((Group.group_name.contains(search)), \
                        (Group.status == int(status)))
        elif search:
            cond = (Group.group_name.contains(search), )
        elif status:
            cond = (Group.status == int(status), )
        else:
            cond = (None, )

        count = Group.select().where(*cond).count()
        groups = Group.select().where(*cond). \
                        paginate(page_index, page_size)

        result = []
        for group in groups:
            node_count = DNodeGroup.select().where(DNodeGroup.group_id == group.id).count()
            result.append(dict(id = group.id,group_name = group.group_name,\
                            plugins = group.plugins, \
                            status = group.status, node_count = node_count))

        self.write(dict(page_index = page_index, count = count,
                        result = result))

class GroupModifyHandler(LoginedRequestHandler):
    def post(self):
        _id = self.get_argument('id')
        group_name = self.get_argument('group_name')
        status = int(self.get_argument('status'))
        plugins = self.get_arguments('plugins')
        plugins = ','.join(plugins)

        ret = Group.update(group_name = group_name, status = status, plugins = plugins).\
                    where(Group.id == _id).execute()
        if ret:
            self.write(dict(status = 1, msg = 'SUCCESS'))
        else:
            self.write(dict(status = 0, msg = 'FAILURE'))

class NodeDelHandler(LoginedRequestHandler):
    def post(self):
        _ids = self.get_arguments('id')

        DNodeGroup.delete().where(DNodeGroup.dnode_id.in_(_ids)).execute()
        ret = DNode.delete().where(DNode.id.in_(_ids)).execute()

        if ret:
            self.write(dict(status = 1, msg = 'SUCCESS'))
        else:
            self.write(dict(status = 0, msg = 'FAILURE'))

class NodeListHandler(LoginedRequestHandler):
    def get(self):
        search = self.get_argument('search', None)
        node_status = self.get_argument('node_status', None)
        group_id = self.get_argument('group_id', None)
        page_index = int(self.get_argument('page_index', 1))
        page_size = int(self.get_argument('page_size', 10))
        unix_time = time.time()

        cond = []
        if search:
            cond.append(DNode.node_name.contains(search))
        if node_status:
            if node_status == '0':
                cond.append(DNode.node_status == node_status)
            elif node_status == '1':
                cond.append(DNode.heartbeat_time >= unix_time - 60)
            elif node_status == '-1':
                cond.append(DNode.heartbeat_time < unix_time - 60)

        dnode_ids = []
        if group_id:
            nodegroup = DNodeGroup.select().where(DNodeGroup.group_id == group_id)
            dnode_ids = [group.dnode_id for group in nodegroup]
            if not dnode_ids:
                self.write(dict(page_index = page_index, count = 0,
                                result = []))
                return

        if dnode_ids:
            cond.append(DNode.id.in_(dnode_ids))

        if not cond:
            cond.append(None)

        count = DNode.select().where(*cond).count()
        dnodes = DNode.select().where(*cond).paginate(page_index, page_size)

        _ids = [node.id for node in dnodes]
        if not _ids:
            self.write(dict(page_index = page_index, count = 0, result = []))
            return

        groups = Group.select(Group, DNodeGroup).join(DNodeGroup).where(DNodeGroup.dnode_id.in_(_ids))
        _map = collections.defaultdict()
        for g in groups:
            dnode_id = g.dnodegroup.dnode_id
            _map.setdefault(dnode_id, []).append(dict(id = g.id, group_name = g.group_name))

        result = [model_to_dict(item) for item in dnodes]
        for item in result:
            sysinfo = __sumeru__.scheduler.agent.get(item['node_id'], {}).get('sysinfo') or {}
            task_list = __sumeru__.scheduler.agent.get(item['node_id'], {}).get('task_list') or []
            sysinfo['task_list'] = task_list

            item['time_diff'] = time.time() - (item.get('heartbeat_time') or 0)
            item['group'] = _map.get(item['id'])
            item['sysinfo'] = sysinfo
            item['task_count'] = len(task_list)

            if item.get('node_status') == 2 and item.get('heartbeat_time') >= unix_time - 60:
                item['node_status'] = 3
            elif item.get('node_status') == 2:
                item['node_status'] = 4

        self.write(dict(page_index = page_index, count = count, result = result))

class NodeModifyHandler(LoginedRequestHandler):
    def post(self):
        _id = self.get_argument('id')
        node_name = self.get_argument('node_name')
        group_ids = self.get_arguments('group_id')
        op = self.get_argument('op')

        if op == 'enable':
            title = '授权'
            ret = DNode.update(node_status = 1).\
                    where(DNode.id == _id).execute()

        with __sumeru__.db.transaction() as txn:
            DNode.update(node_name = node_name).\
                                where(DNode.id == _id).execute()

            DNodeGroup.delete().where(DNodeGroup.dnode_id == _id).execute()
            dnode = DNode(id = _id)
            for group_id in group_ids:
                group = Group(id = group_id)
                DNodeGroup(dnode = dnode, group = group).save()
            txn.commit()
            self.write(dict(status = 1, msg = 'SUCCESS'))

class NodeOPHandler(LoginedRequestHandler):
    def post(self):
        _ids = self.get_arguments('id')
        op = self.get_argument('op')

        if op == 'disable':
            title = '禁用'
            ret = DNode.update(node_token = '', node_status = 0).\
                    where(DNode.id.in_(_ids)).execute()
        elif op == 'enable':
            title = '授权'
            ret = DNode.update(node_status = 1).\
                    where(DNode.id.in_(_ids)).execute()

        if ret:
            self.write(dict(status = 1, msg = title+'SUCCESS'))
        else:
            self.write(dict(status = 1, msg = title+'FAILURE'))

class CronTaskUpsertHandler(LoginedRequestHandler):
    def post(self):
        _id = self.get_argument('id', None)

        task_name = self.get_argument('task_name', '')
        group_id = self.get_argument('group_id', 1)
        layout_id = self.get_argument('layout_id')

        task_type = self.get_argument('task_type', 0)
        is_daemon = self.get_argument('is_daemon', 0)
        is_alarm = self.get_argument('is_alarm', 0)
        is_sendmail = self.get_argument('is_alarm', 0)
        cover_all = self.get_argument('is_cover_all', 0)

        cron = self.get_argument('cron_expr', '@reboot')

        task_desc = self.get_argument('task_desc', '')
        task_code = self.get_argument('task_code', '')

        run_method = self.get_argument('run_method', 1)

        doc = dict(task_name=task_name,
                        task_type=task_type,
                        is_daemon = is_daemon,
                        is_alarm = is_alarm,
                        is_sendmail = is_sendmail,
                        cover_all = cover_all,
                        group_id = group_id,
                        layout_id = layout_id,
                        cron=cron,
                        task_desc=task_desc,
                        task_code=task_code,
                        run_method = run_method,
                        )
        if not _id:
            ct = CronTask(**doc)
            ct.save()
            t = time.time()
            if task_type == '1':
                enable_cron_job(ct.id)
            else:
                run_cron_job(ct.id)
            #print (time.time() - t)
        else:
            CronTask.update(**doc).where(CronTask.id == _id).execute()

        self.write(dict(status = 1, msg = 'SUCCESS'))

class CronTaskDelHandler(LoginedRequestHandler):
    def post(self):
        _ids = self.get_arguments('id')
        for _id in _ids:
            unable_cron_job(_id)

        ret = CronTask.delete().where(CronTask.id.in_(_ids)).execute()
        if ret:
            self.write(dict(status = 1, msg = 'SUCCESS'))
        else:
            self.write(dict(status = 0, msg = 'FAILURE'))

class CronTaskListHandler(LoginedRequestHandler):
    def get(self):
        search = self.get_argument('search', None)
        status = self.get_argument('status', None)
        task_type = self.get_argument('task_type', None)
        page_index = int(self.get_argument('page_index', 1))
        page_size = int(self.get_argument('page_size', 10))

        cond = []
        if task_type in ['0', '1']:
            cond.append(CronTask.task_type == task_type)

        if search:
            cond.append(CronTask.task_name.contains(search))
        if status:
            cond.append(CronTask.status == int(status))
        if not cond:
            cond.append(None)

        count = CronTask.select().where(*cond).count()
        tasks = CronTask.select().where(*cond). \
                        order_by(CronTask.id.desc()). \
                        paginate(page_index, page_size)

        result = []
        for task in tasks:
            time_diff = time.time() - task.update_time.timestamp()
            task = conv_object(model_to_dict(task))
            group = Group.get_or_none(Group.id == task.get('group_id'))
            task['group_name'] = group.group_name if group else ''
            layout = Layout.get_or_none(Layout.id == task.get('layout_id'))
            task['layout_name'] = layout.name if layout else ''
            task['time_diff'] = time_diff
            result.append(task)

        self.write(dict(page_index = page_index, count = count,
                        result = result))


class CronTaskOPHandler(LoginedRequestHandler):
    def post(self):
        _ids = self.get_arguments('id') or []
        op = self.get_argument('OP', self.get_argument('op', ''))

        if op == 'disable':
            title = '禁用'
            for _id in _ids:
                unable_cron_job(_id)
        elif op == 'enable':
            title = '启用'
            for _id in _ids:
                enable_cron_job(_id)
        elif op == 'exec':
            title = '执行'
            _id = self.get_argument('id')
            run_cron_job(_id)
        elif op == 'test':
            title = '测试'
            task_code = self.get_argument('task_code')
            code = base64.b64decode(task_code)
            try:
                scope = {'task': ''}
                exec(code) in scope
            except SyntaxError:
                logger.error('Code Syntax Error')
                self.write(dict(status = 0, msg = title+'FAILURE'))
                return

        self.write(dict(status = 1, msg = title+'SUCCESS'))


class ExecTaskListTopHandler(LoginedRequestHandler):
    def get(self):
        crontask_id = self.get_argument('id')

        result = TaskIns.select().where(TaskIns.crontask_id == crontask_id). \
                        order_by(TaskIns.id.desc()). \
                        paginate(1, 5)

        result = [conv_object(model_to_dict(x)) for x in result]

        self.write(dict(result = result))


class ExecTaskListHandler(LoginedRequestHandler):
    def get(self):
        search = self.get_argument('search', None)
        running_status = self.get_argument('running_status', None)
        crontask_id = self.get_argument('crontask_id', None)
        page_index = int(self.get_argument('page_index', 1))
        page_size = int(self.get_argument('page_size', 10))

        cond = []
        if crontask_id:
            cond.append(TaskIns.crontask_id == int(crontask_id))
        if search:
            cond.append(TaskIns.task_name.contains(search))
        if running_status:
            cond.append(TaskIns.running_status == running_status)
        if not cond:
            cond.append(None)

        count = TaskIns.select().where(*cond).count()
        result = TaskIns.select().where(*cond).order_by(TaskIns.id.desc()). \
                        paginate(page_index, page_size)

        result = [conv_object(model_to_dict(x)) for x in result]
        for item in result:
            group = Group.get_or_none(Group.id == item.get('group_id'))
            item['group_name'] = group.group_name if group else ''

            layout = Layout.get_or_none(Layout.id == item.get('layout_id'))
            item['layout_name'] = layout.name if layout else ''
            item['time_diff'] = time.time() - item.get('start_time')


        self.write(dict(page_index = page_index, count = count,
                        result = result))

class ExecTaskResultHandler(LoginedRequestHandler):
    async def get(self):
        _id = self.get_argument('id')

        ins = TaskIns.get_or_none(TaskIns.id == _id)
        task_id = ins.task_id
        result = await self.tree_tasks(task_id)
        result['result']['status'] = ins.running_status
        result['itemStyle'] = STATUS_COLOR.get(ins.running_status, {})

        self.write(dict(result = result))


class ExecTaskLogHandler(LoginedRequestHandler):
    async def get(self):
        _id = self.get_argument('id')
        skip_id = self.get_argument('skip_id', 0)

        ins = TaskIns.get_or_none(TaskIns.id == _id)
        task_id = ins.task_id
        #tasks = []

        #await self.get_tasks(task_id, r = tasks)
        #task_ids = [item['task_id'] for item in tasks]

        cond = [InsTimeLine.root_task_id == task_id]

        if skip_id:
            cond.append(InsTimeLine.id < int(skip_id))

        logs = InsTimeLine.select().where(*cond).order_by(InsTimeLine.id.desc()).paginate(1, 10)
        logs = [conv_object(model_to_dict(log)) for log in logs]
        skip_id = 0
        if logs:
            skip_id = logs[-1]['id']

        self.write(dict(result = logs, skip_id = skip_id))

class ExecTaskStatusHandler(LoginedRequestHandler):
    async def get(self):
        _ids = self.get_arguments('id')
        _ids = [int(_id) for _id in _ids]
        status = {}
        taskins = TaskIns.select().where(TaskIns.id.in_(_ids))
        for task in taskins:
            task_id = task.task_id
            task_status = await __sumeru__.scheduler.check_task_status(task_id)
            status[task.id] = task_status

        self.write(dict(status = True, result = status))


class ExecTaskOPHandler(LoginedRequestHandler):
    async def post(self):
        _id = self.get_argument('id')
        op = self.get_argument('op')

        ins = TaskIns.get_or_none(TaskIns.id == _id)
        if op == 'exec':
            title = '执行'
            if ins:
                run_cron_job(ins.crontask_id)
                self.write(dict(status = 1, msg = 'SUCCESS'))
            else:
                self.write(dict(status = 0, msg = 'FAILURE NOT FOUND CronTask'))

        elif op == 'stop':
            title = '停止'
            tasks = []
            if ins.running_status not in ['SUCCESS', 'FAILURE', 'CANCELED']:
                await self.get_tasks(ins.task_id, r = tasks)
                for task in tasks:
                    if task.get('parent') == 0 or task.get('status') in \
                            ['SUCCESS', 'FAILURE', 'CANCELED']:
                        continue

                    stop_job(task.get('agent_id'), task.get('task_id'))
                TaskIns.update(running_status = 'CANCELING').where(TaskIns.id == _id).execute()

            self.write(dict(status = 1, msg = 'SUCCESS'))


class SystemSettingsHandler(LoginedRequestHandler):
    def get(self):
        settings = SystemSettings().get_or_none()
        if settings:
            settings = model_to_dict(settings)
            settings['smtp_pass'] = '88888888'
        else:
            settings = {}
        self.write(dict(status = True, result = settings))

    def post(self):
        kwargs = dict((k, v[-1]) for k, v in self.request.arguments.items())
        kwargs.pop('id', None)
        smtp_pass = kwargs.pop('smtp_pass', '88888888')

        for k, v in kwargs.items():
            set_conf(k.upper(), v.decode())
            if k in ['db_driver'] and v:
                set_scheduler(k.upper(), v.decode())

        __sumeru__.scheduler.mq.switch()
        db_switch()
        __sumeru__.scheduler.HA.switch()
        __sumeru__.scheduler.HA_SYNC.switch()

        if smtp_pass != '88888888':
            set_conf('SMTP_PASS', smtp_pass)
            kwargs['smtp_pass'] = smtp_pass

        settings = SystemSettings.get_or_none()
        if not settings:
            SystemSettings(**kwargs).save()
        else:
            SystemSettings.update(**kwargs).execute()

        self.write(dict(status = True))

class SystemOPHandler(LoginedRequestHandler):

    async def get(self):
        init_db()

    async def post(self):
        op = self.get_argument('OP')
        if op == 'CLEAR_TASK_INS':
            TaskIns.delete().execute()
            InsTimeLine.delete().execute()
            await __sumeru__.scheduler.HA.delete('/task_id', recursive=True)
            await __sumeru__.scheduler.HA.delete('/daemon_task', recursive=True)
        elif op == 'CLEAR_TASK_QUEUE':
            # clear running tasks check
            await __sumeru__.scheduler.HA.delete('/running_tasks', recursive=True)

            __sumeru__.scheduler.mq.flush()
        elif op == 'INIT_DB':
            init_db()
        elif op == 'SEND_EMAIL':
            send_email('HELLO WORLD')

        self.write(dict(status = True))

class PluginUploadHandler(LoginedRequestHandler):
    """插件上传"""
    def post(self):
        remark = self.get_argument('remark', '')
        category = self.get_argument('category', '')
        status = self.get_argument('status', 1)

        data = self.request.files['file'][0]
        filename = data.get('filename')

        if not filename.endswith('.zip'):
            self.write(dict(status = False, msg = 'NOT ZIP ARCHIVE'))
            return

        body = data.get('body')
        data_md5 = md5(body).hexdigest()

        plugin_path = os.path.join(__sumeru__.WORKSPACE_PATH, 'plugins_store')
        if not os.path.exists(plugin_path):
            os.makedirs(plugin_path)

        filename = "{}.zip".format(data_md5)
        zip_file = os.path.join(plugin_path, filename)

        with open(zip_file, 'wb') as f:
            f.write(body)

        ex_path = os.sep.join([__sumeru__.PLUGIN_PATH, 'scheduler_plugins', data_md5])
        zip_ref = zipfile.ZipFile(zip_file, 'r')
        zip_ref.extractall(ex_path)
        zip_ref.close()

        if "config.json" not in os.listdir(ex_path):
            os.remove(zip_file)
            self.write(dict(status = False, msg = 'ZIP FILE NOT FOUND config.json, PLEASE CHECK'))
            return

        config_path = os.path.join(ex_path, "config.json")
        with open(config_path, 'r') as f:
            config = json.loads(f.read())
            plugin_name = config.get('plugin_name')
            author = config.get('author')
            version = config.get('version')
            desc = config.get('desc')

            if PluginStore.get_or_none(PluginStore.plugin_name == plugin_name, PluginStore.version == version):
                self.write(dict(status = False, msg = '{} VERSION {} HAS ALREADY EXISTS'.format(plugin_name, version)))
                return

            from sumeru.config import LOGO
            logo = LOGO
            logo_path = os.path.join(ex_path, "logo.png")
            if os.path.exists(logo_path):
                with open(logo_path, 'rb') as f:
                    logo = 'data:image/png;base64,{}'.format(base64.b64encode(f.read()).decode())

            PluginStore.update(is_used = 0).where(PluginStore.plugin_name == plugin_name).execute()

            PluginStore(plugin_name = plugin_name, filename = filename, remark = remark, \
                    category = category, logo = logo, status = status, \
                    author = author, version = version, desc = desc, dtime = str(datetime.now())).save()

            self.write(dict(status = True, msg = 'SUCCESS'))

class PluginSwitchHandler(LoginedRequestHandler):
    """插件切换"""
    def post(self):
        _id = self.get_argument('id')

        plugin = PluginStore.get_or_none(PluginStore.id == _id)

        PluginStore.update(is_used = 0).where(PluginStore.plugin_name == plugin.plugin_name).execute()
        PluginStore.update(is_used = 1).where(PluginStore.id == _id).execute()


        self.write(dict(status = True, msg = "SUCCESS"))


class PluginDownloadHandler(LoginedRequestHandler):
    """插件下载"""
    def get(self):
        _id = self.get_argument('id')
        plugin = PluginStore().get_or_none(PluginStore.id == _id) 
        filename = '{}_{}.zip'.format(plugin.plugin_name, plugin.version)
        with open(os.path.sep.join([__sumeru__.WORKSPACE_PATH, 'plugins_store', plugin.filename]), 'rb') as f:
            self.set_header('Content-Type','application/octet-stream')
            self.set_header('Content-Disposition', 'filename={}'.format(filename))
            self.write(f.read())

class PluginDelHandler(LoginedRequestHandler):
    """插件删除"""
    def post(self):
        _id = self.get_argument('id')
        plugin = PluginStore.get_or_none(PluginStore.id == _id)
        plugins = PluginStore.select().where(PluginStore.plugin_name == plugin.plugin_name)
        for p in plugins:
            fn_path = os.path.sep.join([__sumeru__.WORKSPACE_PATH, 'plugins_store', plugin.filename])
            if os.path.exists(fn_path):
                os.remove(fn_path)

        PluginStore.delete().where(PluginStore.plugin_name == plugin.plugin_name).execute()
        self.write(dict(status = True, msg = "SUCCESS"))


class PluginListHandler(LoginedRequestHandler):
    """插件列表"""
    def get(self):
        search = self.get_argument('search', None)
        status = self.get_argument('status', None)
        plugin_name = self.get_argument('plugin_name', None)
        is_used = int(self.get_argument('is_used', '1'))

        page_index = int(self.get_argument('page_index', 1))
        page_size = int(self.get_argument('page_size', 10))

        cond = [PluginStore.is_used == is_used]
        if plugin_name:
            cond.append(PluginStore.plugin_name == plugin_name)
        if search:
            cond.append(PluginStore.plugin_name.contains(search))
            cond.append(PluginStore.remark.contains(search))
            cond.append(PluginStore.desc.contains(search))

        if status:
            cond.append(PluginStore.status == status)


        count = PluginStore.select().where(*cond).count()
        plugins = PluginStore.select().where(*cond).order_by(PluginStore.dtime.desc()).paginate(page_index, page_size)

        plugins = [conv_object(model_to_dict(p)) for p in plugins]
        self.write(dict(status = True, page_index = page_index, count = count, result = plugins))

class PluginUpdateHandler(LoginedRequestHandler):
    """插件编辑"""
    def post(self):
        _id = self.get_argument('id')
        category = self.get_argument('category', '')
        remark = self.get_argument('remark', '')
        status = self.get_argument('status', 1)

        PluginStore.update(category = category, remark = remark, status = status).where(PluginStore.id == _id).execute()
        self.write(dict(status = True, msg = "SUCCESS"))

class PluginTablesHandler(LoginedRequestHandler):
    """插件表及列"""
    def get(self):
        plugins = __sumeru__.scheduler.decode_map

        result = {}
        for p in plugins:
            if not __sumeru__.db.table_exists(p.lower()): continue
            columns = __sumeru__.db.get_columns(p.lower())
            result[p] = [dict(name = c.name, data_type = c.data_type) for c in columns]

        self.write(dict(status = True, result = result))

class PluginScanDataHandler(LoginedRequestHandler):
    """插件数据"""
    def get(self):
        plugin_name = self.get_argument('plugin_name')
        search = self.get_argument('search', None)
        sort = self.get_argument('sort', None)
        direction = self.get_argument('direction', '')
        page_index = int(self.get_argument('page_index', 1))
        page_size = int(self.get_argument('page_size', 10))

        start = self.get_argument('start', None)
        end = self.get_argument('end', None)

        ins = getattr(__sumeru__.scheduler.decode_map.get(plugin_name), plugin_name)

        search_cond = []
        column_datetime = ''
        columns = __sumeru__.db.get_columns(plugin_name.lower())
        columns_name = [c.name for c in columns]
        if search:
            for c in columns:
                if c.data_type == 'INTEGER':
                    try:
                        search_cond.append((getattr(ins, c.name) == int(search)))
                    except Exception as e:
                        pass
                elif c.data_type == 'DATETIME':
                    column_datetime = c.name
                    pass
                else:
                    search_cond.append((getattr(ins, c.name).contains(search)))

        cond = []
        if search_cond:
            s = search_cond[0]
            for sc in search_cond[1:]:
                s = s | sc

            cond.append(s)

        if start and end:
            start = float(start)
            end = float(end)
            if 'create_time' in columns_name:
                cond.append(getattr(ins, 'create_time') >= datetime.fromtimestamp(start))
                cond.append(getattr(ins, 'create_time') <= datetime.fromtimestamp(end))

        if not cond: cond = [None]

        if sort:
            sort = getattr(ins, sort)
            if direction == 'desc':
                sort = sort.desc()

        count = ins().select().where(*cond).count()
        result = ins().select().where(*cond).order_by(sort).paginate(page_index, page_size)

        result = [conv_object(model_to_dict(r)) for r in result]
        self.write(dict(status = True, page_index = page_index, count = count,  result = result))

class LayoutAddHandler(LoginedRequestHandler):
    """编排添加"""
    async def post(self):
        name = self.get_argument('name')
        layout = self.get_argument('layout')
        l = Layout(layout = layout, name = name)
        l.save()

        layout = json.loads(layout)
        await self.refresh_layout(l.id, layout)
        self.write(dict(status = True, layout_id = l.id))


class LayoutDelHandler(LoginedRequestHandler):
    """编排删除"""
    def post(self):
        _id = self.get_argument('id')
        Layout.delete().where(Layout.id == _id).execute()
        self.write(dict(status = True, msg = 'SUCCESS'))

class LayoutListHandler(LoginedRequestHandler):
    """编排列表"""
    def get(self):
        search = self.get_argument('search', None)
        page_index = int(self.get_argument('page_index', 1))
        page_size = int(self.get_argument('page_size', 10))

        if search:
            cond = (Layout.name.contains(search), )
        else:
            cond = (None, )

        count = Layout.select().where(*cond).count()
        layouts = Layout.select().where(*cond). \
                        order_by(Layout.id.desc()). \
                        paginate(page_index, page_size)

        layouts = [conv_object(model_to_dict(l)) for l in layouts]

        self.write(dict(page_index = page_index, count = count,
                        result = layouts))

class LayoutUpdateHandler(LoginedRequestHandler):
    """编排编辑"""
    async def post(self):
        _id = self.get_argument('id', '')
        name = self.get_argument('name')
        layout = self.get_argument('layout')

        if not _id:
            l = Layout(layout = layout, name = name)
            l.save()

            layout = json.loads(layout)
            await self.refresh_layout(l.id, layout)
            self.write(dict(status = True, layout_id = l.id))
        else:
            Layout.update(name = name, layout = layout, update_time = datetime.now()).where(Layout.id == _id).execute()

            layout = json.loads(layout)
            await self.refresh_layout(_id, layout)

            self.write(dict(status = True, msg = "SUCCESS"))


class IsInstallHandler(LoginedRequestHandler):
    def get(self):
        install_file = os.path.join(__sumeru__.WORKSPACE_PATH, 'install.lock')

        if os.path.exists(install_file):
            self.write(dict(status = True, msg = "SUCCESS"))
        else:
            self.write(dict(status = False, msg = "NOT INSTALLED"))


class InstallHandler(LoginedRequestHandler):
    def post(self):
        op = self.get_argument('op')

        if op == 'test_db':
            # db connect test
            db_host = self.get_argument('db_host')
            db_port = int(self.get_argument('db_port'))
            db_user = self.get_argument('db_user')
            db_password = self.get_argument('db_password')
            db_name = self.get_argument('db_name')
            print (db_host, db_port, db_user, db_password, db_name)
            ret = True
            msg = "SUCCESS"
            try:
                test_db = pymysql.connect(host=db_host, port=db_port, user=db_user, password=db_password)
                test_db.close()
            except Exception as e:
                ret = False
                msg = json.dumps(e.args)

            self.write(dict(status = ret, msg = msg))


        elif op == 'test_redis':
            redis_host = self.get_argument('redis_host')
            redis_port = self.get_argument('redis_port')
            redis_password = self.get_argument('redis_password')
            redis_db = self.get_argument('redis_db', 0)
            redis_driver = 'redis://:{}@{}:{}/{}'.format(redis_password, redis_host, redis_port, redis_db)
            b, msg = __sumeru__.scheduler.mq.check_driver(redis_driver)
            if b: msg = 'SUCCESS'

            self.write(dict(status = b, msg = msg))

        elif op == 'test_etcd':
            etcd_driver = self.get_argument('etcd_driver')
            b, msg = __sumeru__.scheduler.HA_SYNC.check_driver(etcd_driver)
            if b: msg = 'SUCCESS'
            self.write(dict(status = b, msg = msg))

        elif op == 'finish':
            # admin account
            username = self.get_argument('username')
            password1 = self.get_argument('password1')
            password2 = self.get_argument('password2')
            email = self.get_argument('email', '')

            if password1 != password2:
                self.write(dict(status = False, msg = 'password erro'))
                return

            # db conf save to db
            db_host = self.get_argument('db_host')
            db_port = int(self.get_argument('db_port'))
            db_user = self.get_argument('db_user')
            db_password = self.get_argument('db_password')
            db_name = self.get_argument('db_name')
            ret = True
            msg = "SUCCESS"
            try:
                test_db = pymysql.connect(host=db_host, port=db_port, user=db_user, password=db_password)
                test_db.close()
            except Exception as e:
                ret = False
                msg = json.dumps(e.args)

            if not ret:
                self.write(dict(status = ret, msg = msg))
                return

            db_driver = "mysql://{}:{}@{}:{}/{}".format(db_user, db_password, db_host, db_port, db_name)
            set_conf("DB_DRIVER", db_driver)
            set_scheduler("DB_DRIVER", db_driver)
            create_database()
            db_switch()
            init_db(username = username, password = password_md5(password1), email = email)

            # redis save to db
            redis_host = self.get_argument('redis_host')
            redis_port = self.get_argument('redis_port')
            redis_password = self.get_argument('redis_password')
            redis_db = self.get_argument('redis_db', 0)
            redis_driver = 'redis://:{}@{}:{}/{}'.format(redis_password, redis_host, redis_port, redis_db)
            b, msg = __sumeru__.scheduler.mq.check_driver(redis_driver)

            if not b:
                self.write(dict(status = b, msg = msg))
                return

            set_conf('REDIS_DRIVER', redis_driver)
            __sumeru__.scheduler.mq.switch()

            # etcd save to db
            etcd_driver = self.get_argument('etcd_driver')
            b, msg = __sumeru__.scheduler.HA_SYNC.check_driver(etcd_driver)
            if not b:
                self.write(dict(status = b, msg = msg))
                return

            set_conf('ETCD_DRIVER', etcd_driver)
            __sumeru__.scheduler.HA.switch()
            __sumeru__.scheduler.HA_SYNC.switch()

            SystemSettings.update(db_driver = db_driver, redis_driver = redis_driver, etcd_driver = etcd_driver).execute()

            install_file = os.path.join(__sumeru__.WORKSPACE_PATH, 'install.lock')
            with open(install_file, 'w') as f:
                f.write('sumeru\r\n')

            self.write(dict(status = True, msg = 'SUCCESS'))

def sumeru_web():
    current_path = os.path.dirname(__file__)
    application = tornado.web.Application([
        (r"/api/login", LoginHandler),
        (r"/api/logout", LogoutHandler),
        (r"/api/dashboard", DashBoardHandler),
        (r"/api/group/add", GroupAddHandler),
        (r"/api/group/del", GroupDelHandler),
        (r"/api/group/list", GroupListHandler),
        (r"/api/group/modify", GroupModifyHandler),
        (r"/api/dnode/del", NodeDelHandler),
        (r"/api/dnode/list", NodeListHandler),
        (r"/api/dnode/modify", NodeModifyHandler),
        (r"/api/dnode/op", NodeOPHandler),
        (r"/api/crontask/upsert", CronTaskUpsertHandler),
        (r"/api/crontask/del", CronTaskDelHandler),
        (r"/api/crontask/list", CronTaskListHandler),
        (r"/api/crontask/op", CronTaskOPHandler),
        #(r"/api/exectask/add", ExecTaskAddHandler),
        (r"/api/exectask/list", ExecTaskListHandler),
        (r"/api/exectask/listtop", ExecTaskListTopHandler),
        (r"/api/exectask/log", ExecTaskLogHandler),
        (r"/api/exectask/status", ExecTaskStatusHandler),
        (r"/api/exectask/op", ExecTaskOPHandler),
        (r"/api/exectask/result", ExecTaskResultHandler),
        (r"/api/system/settings", SystemSettingsHandler),
        (r"/api/system/op", SystemOPHandler),

        (r"/api/plugin/upload", PluginUploadHandler),
        (r"/api/plugin/switch", PluginSwitchHandler),
        (r"/api/plugin/download", PluginDownloadHandler),
        (r"/api/plugin/del", PluginDelHandler),
        (r"/api/plugin/list", PluginListHandler),
        (r"/api/plugin/update", PluginUpdateHandler),
        (r"/api/plugin/tables", PluginTablesHandler),
        (r"/api/plugin/data", PluginScanDataHandler),

        (r"/api/layout/add", LayoutAddHandler),
        (r"/api/layout/del", LayoutDelHandler),
        (r"/api/layout/list", LayoutListHandler),
        (r"/api/layout/update", LayoutUpdateHandler),

        (r"/api/is_install", IsInstallHandler),
        (r"/api/install", InstallHandler),

        (r'^/(.*?)$', tornado.web.StaticFileHandler, {"path":os.path.join(current_path, "sumeru-web/"), "default_filename":"index.html"})
        ],cookie_secret = '61oETzKXQAGaYdkL5gEmGeJJFuYh7EQnp2XdTP1o/Vo=', static_path=os.path.join(current_path, "sumeru-web/static"))

    application.listen(8888)
    logger.info("     sumeru at: %25s", ":8888")


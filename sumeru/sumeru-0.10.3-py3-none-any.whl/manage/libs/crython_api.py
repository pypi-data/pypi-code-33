#! /usr/bin/env python
#coding=utf-8
from __future__ import print_function, division, absolute_import

import json
import math
import time
import base64
import random
import logging
import itertools
from functools import partial

from .models import *
from .crython.tab import default_tab as tab
from .crython.expression import CronExpression
from .util import make_hash, _task_push

logger = logging.getLogger(__name__)

def pick_workers(group_id, num = 1, cover_all = 0):
    dnodes = DNode.select().join(DNodeGroup).where(DNodeGroup.group_id == group_id, \
                        DNode.heartbeat_time >= time.time() - 60)

    agent_ids = set([item.node_id for item in dnodes])
    if not agent_ids: return
    agent_ids = agent_ids.intersection(set(__sumeru__.scheduler.agent.keys()))
    agents = []
    for agent_id in list(agent_ids):
        agent = __sumeru__.scheduler.agent[agent_id]
        address = agent['address']
        agents.append(dict(agent_id = agent_id, address = address, \
                    task_count = len(agent.get('task_list', []))))

    if not agents: return

    if cover_all:
        return agents

    agents = sorted(agents, key = lambda x:x['task_count'])
    if num > len(agents):
        agents = agents * int(math.ceil(float(num) / len(agents)))

    if num == 1:
        i = random.randint(1, len(agents))
        return [agents[i - 1]]
    else:
        return agents[:num]


def run_cron_job(crontask_id = None, **kwargs):
    t = time.time()
    ct = CronTask.get_or_none(CronTask.id == crontask_id)
    if not ct: return
    

    task_name = ct.task_name
    task_code = base64.b64decode(ct.task_code or '')
    if not task_code:
        task_code = b'task={"PARAM": {}}'
    group_id = ct.group_id
    layout_id = ct.layout_id
    task_type = ct.task_type
    is_daemon = ct.is_daemon
    is_alarm = ct.is_alarm
    cover_all = ct.cover_all    # cover_all must has one component, because multi component not fit cover_all mode
    run_method = ct.run_method

    root_task_id = make_hash()

    try:
        exec(task_code)
        task_data = locals().get('task',None) or {}
        task_data['RUN_METHOD'] = run_method
    except Exception as e:
        logger.error('Code Syntax Error')
        return

    layout = __sumeru__.scheduler.HA_SYNC.read("/layout_id/{}".format(layout_id))
    root_component_id = layout.value

    component = __sumeru__.scheduler.HA_SYNC.read("/component_id/{}".format(root_component_id))
    component = json.loads(component.value)

    root_task = dict(task_id = root_task_id, \
                    root_task_id = root_task_id, \
                    component_id = root_component_id, \
                    group_id = group_id, \
                    parent = 0, \
                    child = [], \
                    finish_child = [], \
                    layout_id = layout_id, \
                    crontask_id = crontask_id, \
                    params = {}, \
                    result = [], \
                    start_time = time.time(), \
                    finish_time = 0, \
                    run_method = run_method, \
                    )

    __sumeru__.scheduler.HA_SYNC.write('/running_tasks/{}'.format(root_task_id), time.time())
    __sumeru__.scheduler.HA_SYNC.write('/task_id/{}'.format(root_task_id), json.dumps(root_task))

    if is_daemon:
        __sumeru__.scheduler.HA_SYNC.write('/daemon_task/{}'.format(root_task_id), root_task_id)

    TaskIns(task_id = root_task_id, task_name = task_name, crontask_id = crontask_id, \
            group_id = group_id, layout_id = layout_id, running_status = 'RUNNING', start_time = time.time()).save()

    run_component(root_task, component, task_data, cover_all = cover_all)

    return dict(status = True, task_id = root_task_id, msg = "")


def run_component(parent_task, component, task_data, cover_all = 0):
    group_id = parent_task['group_id']

    parent_task_id = parent_task['task_id']
    layout_id = parent_task['layout_id']
    root_task_id = parent_task['root_task_id']
    PLUGIN_NAME = component.get('name')
    task_data['PLUGIN_NAME'] = PLUGIN_NAME

    SPLICE = task_data.get('SPLICE', [])
    NGROUP = task_data.get('NGROUP')

    tasks = []
    PARAM = task_data.get('PARAM', {})
    if SPLICE and PARAM and not cover_all:
        PARAM = task_data.pop('PARAM', {})
        args = [PARAM.pop(i) for i in SPLICE]
        dk_params = [x for x in itertools.product(*args)]
        params = []

        for param in dk_params:
            p = {}
            for i, arg in enumerate(args):
                p[SPLICE[i]] = param[i]
            params.append(p)
    
        if NGROUP and len(SPLICE) == 1:
            n = math.ceil(len(params) / float(NGROUP))
            params = [params[i * NGROUP: (i + 1) * NGROUP] for i in range(n)]
            key = SPLICE[0]
            params = [dict(target = [item.get(key) for item in items]) for items in params]

        for param in params:
            param.update(PARAM)
            _task = dict(PARAM = param, TASK_ID = make_hash())
            _task.update(task_data)
            tasks.append(_task)
    else:
        task_data['TASK_ID'] = make_hash()
        tasks = [task_data]

    agents = pick_workers(group_id, num = len(tasks), cover_all = cover_all)
    if not agents:
        TaskIns.update(running_status = 'FAILURE', finish_time = time.time()).where(TaskIns.task_id == root_task_id).execute()

        errmsg = "GROUP:{} NOT FOUND AGENTS".format(group_id)
        logger.warning(errmsg)
        return dict(status = False, task_id = root_task_id, msg = errmsg)


    if cover_all:
        tasks = tasks * len(agents)

        for _task in tasks:
            _task['TASK_ID'] = make_hash()

    task_ids = [item.get('TASK_ID') for item in tasks]
    #parent_task = __sumeru__.scheduler.HA_SYNC.read('/task_id/{}'.format(parent_task_id))
    #parent_task = json.loads(parent_task.value)
    parent_task['child'].extend(task_ids)
    __sumeru__.scheduler.HA_SYNC.write('/task_id/{}'.format(parent_task_id), json.dumps(parent_task))

    for i, agent in enumerate(agents):
        agent_id = agent.get('agent_id')

        _task = tasks[i]
        child_task = dict(task_id = _task['TASK_ID'], \
                        component_id = component['node_id'], \
                        group_id = group_id, \
                        parent = parent_task_id, \
                        root_task_id = root_task_id, \
                        layout_id = layout_id, \
                        child = [], \
                        finish_child = [], \
                        status = 'PENDING', \
                        params = _task, \
                        result = [], \
                        agent_id = agent_id, \
                        start_time = time.time(), \
                        finish_time = 0, \
                        run_method = parent_task['run_method'], \
                        )
        __sumeru__.scheduler.HA_SYNC.write('/task_id/{}'.format(_task['TASK_ID']), json.dumps(child_task))

        _task_push(_task, agent_id = agent_id)


def run_task(task_id, group_id, params):
    agents = pick_workers(group_id, num = 1)
    if not agents:
        logger.warning("GROUP:{} NOT FOUND AGENTS".format(group_id))
        return

    _task_push(params, agent_id = agents[0]['agent_id'])


def stop_job(agent_id, task_id):
    '''
        stop a job
    '''
    task_push = partial(_task_push, agent_id=agent_id)

    task_data = dict(OP = 'STOP', TASK_ID = task_id)
    task_push(task_data)


def unable_cron_job(task_id):
    ct = CronTask.get(CronTask.id == task_id)
    ct.status = 0
    tab.deregister(ct.id)
    return ct.save()

def register_cron_job(crontask_id, expr):
    if not expr: return
    run_cron_job.ctx = 'thread'
    expr = expr.replace('?', '*')
    run_cron_job.cron_expression = CronExpression.new(expr)
    run_cron_job.params = {'crontask_id': crontask_id}

    tab.register(crontask_id, run_cron_job)

def enable_cron_job(task_id):
    ct = CronTask.get(CronTask.id == task_id)
    ct.status = 1
    ct.save()
    register_cron_job(ct.id, ct.cron)


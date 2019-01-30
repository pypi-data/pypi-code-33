#!usr/bin/env python
# coding=utf-8
from sumeru.compatibility import __builtin__
from sumeru.compatibility import ConfigParser

import os
import shutil
from types import ModuleType

conf = ModuleType('__sumeru__')
__builtin__.__sumeru__ = conf

CURRENT_PATH = os.path.dirname(__file__)

SECRET_KEY = 'ed427676-93da-11e8-a2cc-dc5360f1d0ba'

WORKSPACE_PATH  = os.path.join(os.environ['HOME'], '.sumeru')
PLUGIN_PATH  = WORKSPACE_PATH
AGENT_CONF = os.path.join(WORKSPACE_PATH, 'sumeru_agent.conf')
SCHEDULER_CONF = os.path.join(WORKSPACE_PATH, 'sumeru_scheduler.conf')
LOG_PATH = os.path.join(WORKSPACE_PATH, 'logs')

def set_conf(k, v):
    setattr(__builtin__.__sumeru__, k, v)

def set_scheduler(k, v):
    c = ConfigParser()
    c.read(SCHEDULER_CONF)
    if not c.has_section('SCHEDULER'):
        c.add_section('SCHEDULER')
    c.write(open(SCHEDULER_CONF, 'w'))

    c = ConfigParser()
    c.read(SCHEDULER_CONF)
    c.set("SCHEDULER", k, v)
    with open(SCHEDULER_CONF, 'w') as configfile:
        c.write(configfile)


def SET_AGENT_ID(x):
    c = ConfigParser()
    c.read(AGENT_CONF)

    c.set("DEBUG", "AGENT_ID", x)

    with open(AGENT_CONF, 'w') as configfile:
        c.write(configfile)

    set_conf("AGENT_ID", x)

def SET_TOKEN(x):
    c = ConfigParser()
    c.read(AGENT_CONF)

    c.set("DEBUG", "TOKEN", x)
    with open(AGENT_CONF, 'w') as configfile:
        c.write(configfile)

set_conf('SET_AGENT_ID', SET_AGENT_ID)
set_conf('SET_TOKEN', SET_TOKEN)
set_conf('WORKSPACE_PATH', WORKSPACE_PATH)
set_conf('PLUGIN_PATH', PLUGIN_PATH)
set_conf('LOG_PATH', LOG_PATH)
set_conf('SECRET_KEY', SECRET_KEY)

def refresh_options(c, section):
    options = c.options(section)
    for o in options:
        v = c.get(section, o)
        try:
            v = int(v)
        except Exception:
            try:
                v = float(v)
            except Exception:
                pass

        set_conf(o.upper(), v)

def refresh_config(_type = 'scheduler'):
    if not os.path.exists(WORKSPACE_PATH):
        os.makedirs(WORKSPACE_PATH)

    if not os.path.exists(os.path.join(PLUGIN_PATH, 'plugins')):
        os.makedirs(os.path.join(PLUGIN_PATH, 'plugins'))

    if not os.path.exists(os.path.join(WORKSPACE_PATH, 'scheduler_plugins')):
        os.makedirs(os.path.join(WORKSPACE_PATH, 'scheduler_plugins'))

    if not os.path.exists(LOG_PATH):
        os.makedirs(LOG_PATH)

    if not os.path.exists(AGENT_CONF):
        shutil.copyfile(os.sep.join([CURRENT_PATH,'config_example/sumeru_agent.conf']), AGENT_CONF)

    if not os.path.exists(SCHEDULER_CONF):
        shutil.copyfile(os.sep.join([CURRENT_PATH,'config_example/sumeru_scheduler.conf'] ), SCHEDULER_CONF)

    if _type == 'agent':
        c = ConfigParser()
        c.read(AGENT_CONF)
        refresh_options(c, "DEBUG")
        refresh_options(c, "COMMON")
    else:
        c = ConfigParser()
        c.read(SCHEDULER_CONF)
        sections = c.sections()
        for section in sections:
            refresh_options(c, section)


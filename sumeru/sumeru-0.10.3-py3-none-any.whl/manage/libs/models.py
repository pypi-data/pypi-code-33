#! /usr/bin/env python
#coding=utf-8

from __future__ import print_function, division, absolute_import
from datetime import datetime
import logging

import pymysql
from peewee import *
from playhouse.db_url import connect
from playhouse.pool import PooledMySQLDatabase
from playhouse.shortcuts import model_to_dict

logger = logging.getLogger(__file__)

from sumeru.manage.conf import set_conf

db_proxy = Proxy()

if __sumeru__.DB_DRIVER.startswith("mysql://"):
    db = PooledMySQLDatabase(None)
else:
    try:
        db = SqliteDatabase('sumeru.db')
        db_proxy.initialize(db)
    except Exception as e:
        db = PooledMySQLDatabase(None)

set_conf('db', db)

def db_prepare(func):
    def d_func(*args, **kargs):
        try:
            #try:
            #    if __sumeru__.db.is_closed():
            #        __sumeru__.db.connect()
            #    else:
            #        user = User().get_or_none()
            #except Exception as e:
            #    logger.warning("db_prepare closed {}".format(e))
            #    __sumeru__.db.close()
            #    __sumeru__.db.connect()

            ret = func(*args, **kargs)

            return ret
        except Exception as e:
            logger.error(e)
            return None

    return d_func

from functools import wraps

def database_connection(func):
    @wraps(func)
    def inner(*args, **kwargs):
        if __sumeru__.db.is_closed():
            __sumeru__.db.connect()
        try:
            return func(*args, **kwargs)
        finally:
            if not __sumeru__.db.is_closed():
                __sumeru__.db.close()

    return inner


def conv_object(d):
    if isinstance(d, (datetime,)):
        return str(d)
    if isinstance(d, (bytes,)):
        return d.decode()
    elif isinstance(d, (list, tuple)):
        return [conv_object(x) for x in d]
    elif isinstance(d, dict):
        return dict([(conv_object(k), conv_object(v)) for k, v in d.items()])
    else:
        return d

class BaseModel(Model):
    class Meta:
        database = db_proxy

class User(BaseModel):
    id = AutoField()
    username = CharField(unique = True)
    password = CharField()
    enable = IntegerField(default = 1)
    create_time = DateTimeField(default = datetime.now)


class CronTask(BaseModel):
    id = AutoField() 
    task_name = CharField(default='')
    task_code = TextField(default='')
    task_desc = TextField(default='')
    layout_id = IntegerField(null = True)
    group_id = IntegerField(null=True)
    cron = CharField(null=True)

    task_type = IntegerField(default=0)  #立即执行任务0，定时任务1
    is_daemon = IntegerField(default=0) #常驻选项
    is_alarm = IntegerField(default=0)  #常驻选项 生命周期结束告警
    is_sendmail = IntegerField(default=0)  #0 不发送，1 发送
    run_method = IntegerField(default = 1)
    cover_all = IntegerField(default = 0)
    
    count = IntegerField(default=0)
    status = IntegerField(default=0)
    create_time = DateTimeField(default=datetime.now)
    update_time = DateTimeField(default=datetime.now)

class TaskIns(BaseModel):
    id = AutoField()
    task_id = CharField()
    task_name = CharField(null = True)
    crontask_id = IntegerField()
    group_id = IntegerField(null=True)
    layout_id = IntegerField(null = True)

    running_status = CharField(default = 0)
    start_time = DoubleField(default = 0)
    finish_time = DoubleField(default = 0)

class InsTimeLine(BaseModel):
    id = AutoField()
    task_id = CharField(null = True)
    root_task_id = CharField(null = True)
    data = TextField(null = True)
    create_time = DateTimeField(default = datetime.now)

class DNode(BaseModel):
    id = AutoField() 
    node_id = CharField()
    node_name = CharField(null = True)
    node_addr = CharField(null=True)
    node_desc = TextField(null=True)
    node_token = CharField(null=True)
    node_key = CharField(null=True)
    heartbeat_time = DoubleField(null=True)
    task_count = IntegerField(default=0)
    node_status =  IntegerField(default = 0)
    plugin_status =  TextField(null=True)
    reg_time = DateTimeField(null=True)

class Group(BaseModel):
    id = AutoField(primary_key = True)
    group_name = CharField()
    status = IntegerField(default = 1)
    group_desc = TextField(default = '')
    plugins = TextField(default = '')


class DNodeGroup(BaseModel):
    id = AutoField() 
    dnode = ForeignKeyField(DNode)
    group = ForeignKeyField(Group)

    class Meta:
        indexes = (
            (('dnode_id', 'group_id'), True),
        )

class SystemSettings(BaseModel):
    id = AutoField(primary_key = True)
    db_url = CharField(null = True)
    mq_url = CharField(null = True)
    db_driver = CharField(null = True)
    etcd_driver = CharField(null = True)
    redis_driver = CharField(null = True)
    smtp_host = CharField(null = True)
    smtp_port = CharField(null = True)
    smtp_user = CharField(null = True)
    smtp_pass = CharField(null = True)
    mail_list = CharField(null = True)


class PluginStore(BaseModel):
    id = AutoField(primary_key = True)
    plugin_name = CharField()
    version = CharField(null = True)
    author = CharField(null = True)
    remark = CharField(null = True)
    category = CharField(null = True)
    logo = TextField(null = True)
    desc = CharField(null = True)
    filename = CharField(null = True)
    dtime = CharField(null = True)
    status = IntegerField(default = 1)
    is_used = IntegerField(default = 1)


# 编排
class Layout(BaseModel):
    id = AutoField(primary_key = True)
    name = TextField(null = True)
    layout = TextField(null = True)
    update_time = DateTimeField(default = datetime.now)


@database_connection
def load_settings():
    try:
        settings = SystemSettings.get_or_none()
        if settings:
            for k, v in model_to_dict(settings).items():
                if k == '_id': continue
                set_conf(k.upper(), v)
    except Exception as e:
        pass

def create_database():
    try:
        if __sumeru__.DB_DRIVER.startswith("mysql://"):
            driver, db_name = __sumeru__.DB_DRIVER[8:].split('/')
            host, p = driver.split('@')[1].split(':')
            user, pw = driver.split('@')[0].split(':')

            connection = pymysql.connect(host=host, port=int(p), user=user, password=pw)

            with connection.cursor() as cursor:
                cursor.execute('create database if not exists {} character set utf8'.format(db_name))
    except:
        pass

def alert_table():
    try:
        if __sumeru__.DB_DRIVER.startswith("mysql://"):
            driver, db_name = __sumeru__.DB_DRIVER[8:].split('/')
            host, p = driver.split('@')[1].split(':')
            user, pw = driver.split('@')[0].split(':')

            connection = pymysql.connect(host=host, port=int(p), user=user, password=pw, db = db_name)

            with connection.cursor() as cursor:
                cursor.execute('alter table pluginstore modify column logo LONGTEXT')
                cursor.execute('alter table instimeline modify column data LONGTEXT')
    except:
        pass

    pass

def db_connect():
    try:
        if __sumeru__.DB_DRIVER.startswith("mysql://"):
            create_database()
            driver, db_name = __sumeru__.DB_DRIVER[8:].split('/')
            host, p = driver.split('@')[1].split(':')
            user, pw = driver.split('@')[0].split(':')
            __sumeru__.db = PooledMySQLDatabase(db_name, host=host, port=int(p), user=user, password = pw, max_connections = None, stale_timeout=5, timeout = 30)
        else:
            __sumeru__.db = SqliteDatabase("sumeru.db")

        db_proxy.initialize(__sumeru__.db)
    except Exception as e:
        logger.warning(e)
        return

db_switch = db_connect

@database_connection
def init_db():
    create_database()
    db.drop_tables([CronTask,Group,DNode,DNodeGroup, SystemSettings, PluginStore, TaskIns, InsTimeLine, Layout])
    db.create_tables([CronTask,Group,DNode,DNodeGroup, SystemSettings, PluginStore, TaskIns, InsTimeLine, Layout])
    alert_table()

    db.drop_tables([User])
    db.create_tables([User])
    password = "09de2152139ed036151e252bb5df3574"
    user = User(username = "admin", password = password)
    user.save()

db_connect()






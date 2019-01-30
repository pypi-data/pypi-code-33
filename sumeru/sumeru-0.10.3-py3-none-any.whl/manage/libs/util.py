from __future__ import print_function, division, absolute_import
import os
import json
import socket
import hashlib
try:
    import pip._internal as pip
except:
    import pip
import importlib
import datetime
from datetime import datetime
import hashlib
import smtplib
from email.mime.text import MIMEText
from email.header import Header

def _task_push(task_entity, agent_id):
    '''
    push a task_entity
    '''
    key = datetime.now().strftime("task_count_%Y-%m-%d %H:%M:%S")
    seconds = int(key.split(":")[-1])
    seconds = str(int(seconds / 5)).zfill(2)
    key = key[:-2] + seconds

    task_count = __sumeru__.scheduler.mq.inc(key)
    __sumeru__.scheduler.mq.set('tps_current_task_count', task_count)
    if task_count > int(__sumeru__.scheduler.mq.get('tps_max_task_count') or 0):
        __sumeru__.scheduler.mq.set('tps_max_task_count', task_count)

    return __sumeru__.scheduler.mq.rpush(agent_id, json.dumps(task_entity))


def make_hash():
    '''
        make hash randomly
    '''
    return hashlib.sha1(os.urandom(24)).hexdigest()


def make_token(agent_id, secret):
    '''
        make hash randomly
    '''
    k = agent_id + secret
    return hashlib.sha256(k.encode()).hexdigest()

def load_json(json_path):
    '''
    load json from path
    '''
    with open(json_path) as json_raw:
        return json.loads(json_raw.read())


def pip_install(package):
    '''
    pip install in code
    '''
    pip.main(['install', package])

def pip_check(package):
    '''
    python package check in code
    '''

    package_list = map(lambda x:x.project_name,pip.utils.misc.get_installed_distributions())
    return package in package_list

def import_check(package):
    '''
    check package installed through import
    '''
    try:
        importlib.import_module(package)
    except ImportError:
        return False
    else:
        return True

def check_remote_port(r_ip, r_port):
    '''
    Check if remote port is open
    '''

    check_remote_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        check_remote_socket.connect((r_ip, int(r_port)))
        check_remote_socket.shutdown(2)
        return True
    except Exception as _:
        return False
    finally:
        check_remote_socket.close()

def send_email(msg_text,title=u'[Sumeru] TASK STATUS'):
    try:
        msg = MIMEText(msg_text, 'plain', 'utf-8')
        FROM_ADDR = __sumeru__.SMTP_USER
        SMTP_PASSWORD = __sumeru__.SMTP_PASS
        SMTP_HOST = __sumeru__.SMTP_HOST
        SMTP_PORT = __sumeru__.SMTP_PORT
        TO_ADDR = __sumeru__.MAIL_LIST
        msg['To'] = TO_ADDR
        msg['Subject'] = Header(title, 'utf-8').encode()
        email_sender = smtplib.SMTP(SMTP_HOST, SMTP_PORT)
        email_sender.login(FROM_ADDR, SMTP_PASSWORD)
        email_sender.sendmail(FROM_ADDR,TO_ADDR.split(','), msg.as_string())
        email_sender.close()
    except Exception as e:
        pass

def get_plugins(folder = 'plugins'):
    plugins_local = []
    for plugin_dir in os.listdir(os.sep.join([__sumeru__.PLUGIN_PATH, folder])):
        p = os.sep.join([__sumeru__.PLUGIN_PATH, folder, plugin_dir])
        if not os.path.isdir(p): continue

        f_config = os.sep.join([p, 'config.json'])
        if not os.path.exists(f_config): continue

        plugins_local.append(plugin_dir)

    return plugins_local


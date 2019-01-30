from datetime import datetime

from cpbox.app.appconfig import appconfig
from cpbox.tool import concurrent
from cpbox.tool import timeutil

import time
import os
import threading
import json
import logging
import socket

try:
    from threading import get_ident
except ImportError:
    from thread import get_ident

event_logger = logging.getLogger('event-log')
local_ip = socket.gethostbyname(socket.gethostname())

log_worker = concurrent.Worker(2)
# This is what we want: 2018-11-12T15:34:34+08:00 117.50.2.88 15051.50683 cp mid-call {"fail":0,"service":"id_service.next_id","rt_1":1.1670589447021,"rt":1.1730194091797,"env":"prod"}
# python strftime can not print timezone as +08:00
# logstash grok ISO8601_TIMEZONE will let this go: 2018-11-12T15:36:46+0800 172.16.1.150 28114.139798089959232 None test {"env": "dev", "time": "2018-11-12 15:36:46.359019"}
# ${time_iso_8601} ${client_ip} ${pid}.${rnd/thread_id} {$app_name} ${event_key} ${payload_json_encoded}
def add_event_log(event_key, payload):
    payload['env'] = appconfig.get_env()
    time = timeutil.local_now_ios8061_str()
    msg = '%s %s %s.%s %s %s %s' % (time, local_ip, os.getpid(), get_ident(), appconfig.get_app_name(), event_key, json.dumps(payload))
    log_worker.submit(event_logger.info, msg)

def log_func_call(func, *args, **kwargs):
    def timed(*args, **kw):
        start = time.time() * 1000
        result = func(*args, **kw)
        payload = {}
        payload['name'] = func.__name__
        payload['rt'] = time.time() * 1000 - start
        add_event_log('func-call', payload)
        return result
    return timed

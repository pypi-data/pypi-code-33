import logging
import uuid
import requests
import collections
import json
import time
from pathlib import Path
from typing import Dict, Any, Optional, Callable

import sentry_sdk
from sentry_sdk.integrations.logging import LoggingIntegration, ignore_logger
import logzio.handler
from logdna import LogDNAHandler

# sentry_sdk.init("https://1830d21cd41c4e00ac39aaade813c60d@sentry.io/1382546")

BASE_URL = "https://labs.1a23.com/telemetry_config/"

device_id: Optional[str] = None
instances: Dict[str, Any] = {}


class JSONEncoder(json.JSONEncoder):
    def default(self, o):
        return repr(o)

class TelemetryProvider:
    def set_metadata(data: Dict[str, any]):
        pass

class SentryErrorReporting(TelemetryProvider):
    def __init__(self, options: Dict[str, Any]):
        del options['provider']
        if 'enable' in options:
            del options['enable']
        if 'available' in options:
            del options['available']
        token = options.pop('token')
        integrations = []
        if not options.get('capture_logs'):
            integrations.append(LoggingIntegration(level=logging.ERROR))
        if 'capture_logs' in options:
            del options['capture_logs']
        if 'ignored_loggers' in options:
            for logger in options['ignored_loggers']:
                ignore_logger(logger)
            del options['ignored_loggers']

        sentry_sdk.init(dsn=token, integrations=integrations,
                        **options)

        with sentry_sdk.configure_scope() as scope:
            scope.user = {'id': get_device_id()}

    def set_metadata(self, data: Dict[str, any]):
        with sentry_sdk.configure_scope() as scope:
            for key, value in data.items():
                scope.set_tag(key, str(value))


class LogzLogAnalysis(TelemetryProvider):
    def __init__(self, options: Dict[str, Any], instance: str):
        token = options['token']
        server = options['server']
        self.hdlr: logzio.handler.LogzioHandler = \
            logzio.handler.LogzioHandler(
                token, logzio_type=instance, url=server
            )
        # self.hdlr.format_message = \
        #     self.wrap_format_message(self.hdlr.format_message)

        logging.getLogger('').addHandler(self.hdlr)

        self.metadata = {'device_id': get_device_id()}
        self.hdlr.setFormatter(logging.Formatter(json.dumps(self.metadata)))
    
    def set_metadata(self, data: Dict[str, any]):
        self.metadata.update(data)
        self.hdlr.setFormatter(logging.Formatter(json.dumps(self.metadata)))

    def wrap_format_message(self, fn: Callable):
        def format_message(message: logging.LogRecord):
            d = fn(message)
            args = self.json_obj_escape(message.args)
            if not isinstance(args, list):
                args = [args]
            for idx, i in enumerate(args):
                i_type = type(i).__name__
                d['arg_%s_%s' % (idx, i_type)] = i
            if not isinstance(message.msg, str):
                obj = self.json_obj_escape(message.msg)
                obj_type = type(obj).__name__
                d['msg_' + obj_type] = obj
            return d
        return format_message

    def json_obj_escape(self, obj):
        if isinstance(obj, tuple):
            obj = list(obj)
        if isinstance(obj, (str, bool, float, int, type(None))):
            return obj
        elif isinstance(obj, list):
            return list(map(self.json_obj_escape, obj))
        elif isinstance(obj, dict):
            return {self.json_obj_escape(k): self.json_obj_escape(v) for k, v in obj.items()}
        else:
            return repr(obj)


class LogglyLogAnalysis(LogzLogAnalysis):
    def __init__(self, options: Dict[str, Any], instance: str):
        token = "token"
        server = options['url'] + instance + "/"
        self.hdlr: logzio.handler.LogzioHandler = \
            logzio.handler.LogzioHandler(
                token, logzio_type=instance, url=server
            )
        self.hdlr.format_message = \
            self.wrap_format_message(self.hdlr.format_message)
        self.patch_get_message(self.hdlr.logzio_sender)

        self.hdlr.logzio_sender.url = server

        logging.getLogger('').addHandler(self.hdlr)

        self.metadata = {'device_id': get_device_id()}
        self.hdlr.setFormatter(logging.Formatter(json.dumps(self.metadata)))

    @staticmethod
    def patch_get_message(sender: logzio.sender.LogzioSender):
        def patched_get_msg():
            if not sender.queue.empty():
                return [sender.queue.get()]
            return []
        sender._get_messages_up_to_max_allowed_size = patched_get_msg

    def sanitize_key(self, key: str):
        return key.replace(' ', '_').replace('.', '_')

    def set_metadata(self, data: Dict[str, any]):
        data = {self.sanitize_key(key): value for key, value in data.items()}
        self.metadata.update(data)
        self.hdlr.setFormatter(logging.Formatter(json.dumps(self.metadata)))


class LogDNALogAnalysis(TelemetryProvider):
    def __init__(self, options: Dict[str, Any], instance: str):
        key = options['token']
        options = {"app": instance, "hostname": get_device_id(), 
                   "include_standard_meta": True}

        self.hdlr = LogDNAHandler(key, options)
        self.meta = {}
        self.patch_emit(self.hdlr)

        logging.getLogger('').addHandler(self.hdlr)

    def set_metadata(self, data: Dict[str, any]):
        self.meta.update(data)
    
    def patch_emit(provider, self):
        def emit(record):
            msg = self.format(record)
            record = record.__dict__
            opts = {}
            if 'args' in record:
                opts = record['args']
            
            if self.include_standard_meta:
                if isinstance(opts, tuple):
                    opts = {}
                if 'meta' not in opts:
                    opts['meta'] = {}
                for key in ['name', 'pathname', 'lineno']:
                    opts['meta'][key] = record[key]
                opts['meta'].update(provider.meta)
                if isinstance(record['args'], tuple):
                    opts['meta'].update(
                        {("arg_%s" % idx): i for idx,
                         i in enumerate(record['args'])}
                    )

            message = {
                'hostname': self.hostname,
                'timestamp': int(time.time() * 1000),
                'line': msg,
                'level': record['levelname'] or self.level,
                'app': self.app or record['module'],
                'env': self.env
            }
            if not isinstance(opts, tuple):
                if 'level' in opts:
                    message['level'] = opts['level']
                if 'app' in opts:
                    message['app'] = opts['app']
                if 'hostname' in opts:
                    message['hostname'] = opts['hostname']
                if 'env' in opts:
                    message['env'] = opts['env']
                if 'timestamp' in opts:
                    message['timestamp'] = opts['timestamp']
                if 'meta' in opts:
                    if self.index_meta:
                        message['meta'] = self.sanitizeMeta(opts['meta'])
                    else:
                        message['meta'] = json.dumps(
                            opts['meta'], cls=JSONEncoder)

            self.bufferLog(message)
        self.emit = emit


def init(instance: str, patch: Dict[str, Any]={}):
    resp = requests.get(BASE_URL + instance + ".json")
    if resp.status_code != 200:
        resp.raise_for_status()
    config: Dict[str, Any] = resp.json()
    config = update(config, patch)

    if not isinstance(config, dict):
        raise ValueError()

    for key, val in config.items():
        if not val.get('enable', False) or not val.get('available', False):
            continue
        instances[key] = setup_instance(val, instance)


def update(d, u):
    for k, v in u.items():
        if isinstance(v, collections.Mapping):
            d[k] = update(d.get(k, {}), v)
        else:
            d[k] = v
    return d


def setup_instance(config: Dict[str, Any], instance: str) -> TelemetryProvider:
    provider = config.get('provider', None)
    if provider == 'sentry':
        return SentryErrorReporting(config)
    elif provider == 'logz':
        return LogzLogAnalysis(config, instance)
    elif provider == 'loggly':
        return LogglyLogAnalysis(config, instance)
    elif provider == 'logdna':
        return LogDNALogAnalysis(config, instance)
    else:
        return TelemetryProvider()


def get_device_id() -> str:
    global device_id

    # if no machine ID file saved, generate one, and save it
    # otherwise, get the ID from the file.
    if device_id:
        return device_id

    path: Path = Path.home() / '.1a23_telemetry_device_id'

    if path.exists():
        device_id = path.read_text()
        return device_id

    device_id = str(uuid.uuid4())
    path.write_text(device_id)
    return device_id


def set_metadata(data: Dict[str, any]):
    for i in instances.values():
        i.set_metadata(data)

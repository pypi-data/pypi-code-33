import logging
import re
from urllib.parse import urlparse

# noinspection PyPackageRequirements
import statsd

from tracuni.misc.select_coroutine import (
    IOLoop,
    PeriodicCallback,
)
from tracuni.define.type import (
    StatsdOptions,
)
if not IOLoop:
    import asyncio

ERROR_NOT_CONNECTED = "StatsD is not available!"
MSG_RESPONSE = '%s.response,code=%d'
MSG_EXCEPTION = '%s.exception,code=%d'
MSG_REQUEST = '%s.http_request,url=%s,code=%d'
MSG_METHOD_APIKEY = '%s.method_apikey,method=%s,code=%d,apikey=%s'
check_http_prefix = re.compile(r'^http')


def run_later_if_enabled(fn):
    def decorated(self, *args, **kwargs):
        def wrapper():
            try:
                fn(self, *args, **kwargs)
            except Exception as e:
                logging.error(e)

        if self.enable:
            if self.run_later:
                if IOLoop:
                    IOLoop.current().spawn_callback(
                        wrapper
                    )
                else:
                    asyncio.ensure_future(wrapper())
            else:
                return wrapper()
    return decorated


class StatsD:

    def __init__(self, config):
        self.run_later = config.get('run_later', True)
        self.enable = config.get('enable', False)
        self.logging = config.get('logging', False)
        self.config = {
            'host': config.get('host', 'localhost'),
            'port': config.get('port', 8125),
            'sample_rate': 1,
            'disabled': not self.enable,
        }
        self.name = config.get('prefix', 'svc_api')
        self.hb = None
        self.hb_interval = (config.get('hb_interval', 30) or 30) * 1000

    def connect(self):
        if not self.logging:
            logger_timer = logging.getLogger(
                'statsd.client.Timer'
            )
            logger_timer.propagate = False
            logger_counter = logging.getLogger(
                'statsd.client.Counter'
            )
            logger_counter.propagate = False
            logger_connection = logging.getLogger(
                'statsd.connection.Connection'
            )
            logger_connection.propagate = False
            logger_connection.setLevel(logging.CRITICAL)

        try:
            statsd.Connection.set_defaults(**self.config)
            statsd.Client(name=self.name)
            self.hb = statsd.Counter(self.name)
            if PeriodicCallback:
                PeriodicCallback(
                    callback=self.heartbeat,
                    callback_time=self.hb_interval
                ).start()
            else:
                loop = asyncio.get_event_loop()
                task = asyncio.ensure_future(self.heartbeat())
                loop.call_later(self.hb_interval, task.cancel)
        except Exception as e:
            self.enable = False
            logging.error(e)
            logging.error(ERROR_NOT_CONNECTED)
        return

    def heartbeat(self):
        if self.enable:
            self.hb.increment('heartbeat')

    @run_later_if_enabled
    def send_gauge(self, key, value):
        gauge = statsd.Gauge(self.name)
        gauge.send(key, value)

    @run_later_if_enabled
    def exception(self, code):
        statsd.increment(MSG_EXCEPTION % (self.name, code))

    @run_later_if_enabled
    def response(self, code):
        statsd.increment(MSG_RESPONSE % (self.name, code))

    @run_later_if_enabled
    def http_request(self, url, code):
        statsd.increment(MSG_REQUEST % (self.name, url, code))

    @run_later_if_enabled
    def method_apikey(self, method, code, apikey):
        statsd.increment(MSG_METHOD_APIKEY % (self.name, method, code, apikey))

    def start_timer(self):
        if self.enable:
            timer = statsd.Timer(self.name)
            timer.start()
            return timer

    @run_later_if_enabled
    def stop_timer(self, timer, label):
        if timer:
            timer.stop(label)

    @run_later_if_enabled
    def send_timer(self, name, value):
        timer = statsd.Timer(self.name)
        timer.send(name, value)

    @staticmethod
    def read_statsd_configuration(statsd_conf):
        statsd_enable = bool(statsd_conf.enable)
        statsd_url = statsd_conf.url
        statsd_url = urlparse(
            statsd_url
            if check_http_prefix.match(statsd_url)
            else 'https://{}'.format(statsd_url)
        )

        statsd_is_configured = bool(statsd_url) and statsd_enable
        if statsd_is_configured and not statsd_url.hostname:
            statsd_is_configured = False
            logging.error('Incorrect statsd url')

        # noinspection PyProtectedMember
        updated_conf = statsd_conf._asdict()
        updated_conf.update({
            'enable': statsd_is_configured,
            'host': statsd_url.hostname,
            'port': statsd_url.port,
        })
        statsd_conf = StatsdOptions(**updated_conf)

        return statsd_conf

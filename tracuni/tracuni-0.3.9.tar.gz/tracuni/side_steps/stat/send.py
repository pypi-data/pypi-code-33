import re

import aiozipkin.transport as azt
import aiozipkin.constants as azc
import logging

from .adapter import StatsD
from tracuni.misc.select_coroutine import get_coroutine_decorator
async_decorator = get_coroutine_decorator()


STATS_CLEAN_NAME_RE = re.compile('[^0-9a-zA-Z_.-]')
STATS_CLEAN_TAG_RE = re.compile('[^0-9a-zA-Z_=.-]')


class TracerTransport(azt.Transport):
    # noinspection PyProtectedMember
    def __init__(
            self,
            logging_conf,
            statsd_conf,
            loop,
            use_tornado=False,
    ):
        tracer_url = logging_conf.url
        send_interval = logging_conf.send_interval
        super(TracerTransport, self).__init__(
            tracer_url,
            send_interval=send_interval,
            loop=loop
        )
        self.loop = loop
        self.__tracer = logging_conf.name
        self.use_tornado = use_tornado

        statsd_conf = StatsD.read_statsd_configuration(statsd_conf)

        self.stats = None
        if statsd_conf.enable:
            self.stats = StatsD(statsd_conf._asdict())
            self.stats.connect()
        self.statsd_is_configured = statsd_conf.enable and self.stats

    @async_decorator
    def _send(self):
        data = self._queue[:]

        try:
            if self.statsd_is_configured:
                yield self._send_to_statsd(data)
        except Exception as e:
            logging.exception(e)

        try:
            if self.__tracer == 'zipkin':
                yield super(TracerTransport, self)._send()
            else:
                self._queue = []
        except Exception as e:
            logging.exception(e)

    @async_decorator
    def _send_to_statsd(self, data):
        if self.stats:
            for rec in data:
                tags = []
                t = rec['tags']
                if azc.HTTP_PATH in t and 'kind' in rec:
                    name = 'http'
                    if rec["kind"] == 'SERVER':
                        tags.append(('kind', 'in'))
                    else:
                        tags.append(('kind', 'out'))

                    copy_tags = {
                        azc.HTTP_STATUS_CODE: 'status',
                        azc.HTTP_METHOD: 'method',
                        azc.HTTP_HOST: 'host',
                        'api.key': 'api_key',
                        'api.method': 'api_method',
                        'api.code': 'api_code',
                        'api_merc.code': 'api_merc_code',
                        'peer.host': 'host',
                        'http.method': 'method',
                        'http.status': 'status',
                    }
                    for tag_key, tag_name in copy_tags.items():
                        if tag_key in t:
                            tags.append((tag_name, t[tag_key]))

                elif rec['name'].lower().startswith('db:'):
                    name = 'db'
                    tags.append(('kind', rec['name'][len('db:'):]))
                elif rec['name'].lower().startswith('redis:'):
                    name = 'redis'
                    tags.append(('kind', rec['name'][len('redis:'):]))
                elif rec['name'].lower().startswith('amqp:'):
                    name = 'amqp'
                    if rec["kind"] == 'SERVER':
                        tags.append(('kind', 'in'))
                    else:
                        tags.append(('kind', 'out'))

                elif rec['name'].lower() == 'sleep':
                    name = 'sleep'
                else:
                    name = rec['name']

                name = name.replace(' ', '_')

                if len(tags) > 0:
                    for tag in tags:
                        t = tag[1].replace(':', '-')
                        t = STATS_CLEAN_TAG_RE.sub('', t)
                        name += ',' + tag[0] + "=" + t
                self.stats.send_timer(name, int(round(rec["duration"] / 1000)))
                self.stats.send_timer('op', 1000)

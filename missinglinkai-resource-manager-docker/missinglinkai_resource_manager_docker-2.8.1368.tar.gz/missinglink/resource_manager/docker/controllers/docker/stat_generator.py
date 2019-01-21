import asyncio
import logging

from dateutil import parser

logger = logging.getLogger(__name__)


class StatGenerator:
    def __init__(self, container):
        self.container = container
        self.id = self.container.name

    def _keep_reading_stats(self):
        self.container.reload()
        if self.container.status == 'exited':
            logger.debug('%s:STATS: No more stats: %s', self.id, self.container.status)
            return False

        return True

    async def __anext__(self):
        await asyncio.sleep(0)
        while self._keep_reading_stats():
            stat = self.container.stats(stream=False)
            stat_obj = self._stats(stat)

            if stat_obj is None:

                if not self._keep_reading_stats():
                    break
                logger.warning('%s:STATS: Empty Stats, state: %s', self.id, self.container.status)
                continue

            logger.debug('%s:STAT: Sending stats %s', self.id, stat_obj)
            return stat_obj
        logger.debug('%s:STATS: DONE Sending stats', self.id)
        raise StopAsyncIteration

    def __aiter__(self):
        logger.debug('%s:STATS: start', self.id)
        return self

    def _stats(self, stat):
        if not ('read' in stat and parser.parse(stat['read']).year != 1):
            return

        # https://github.com/moby/moby/blob/eb131c5383db8cac633919f82abad86c99bffbe5/cli/command/container/stats_helpers.go#L175
        def mem_usage():
            memstat = stat.get('memory_stats', {})
            return memstat.get('usage', 0), memstat.get('limit', 0)

        # https://github.com/moby/moby/blob/eb131c5383db8cac633919f82abad86c99bffbe5/cli/command/container/stats_helpers.go#L175
        def cpu_usage():
            cpu_percent = 0.0
            pre_cpu_stat = stat.get('precpu_stats', {})
            pre_cpu = pre_cpu_stat.get('cpu_usage', {}).get('total_usage', 0)
            pre_system = pre_cpu_stat.get('system_cpu_usage', 0)
            cur_system = stat.get('cpu_stats', {}).get('system_cpu_usage', 0)
            cur_cpu = stat.get('cpu_stats', {}).get('cpu_usage', {}).get('total_usage', 0)
            cpu_delta = cur_cpu - pre_cpu
            system_delta = cur_system - pre_system
            cpu_count = len(stat.get('cpu_stats', {}).get('cpu_usage', {}).get('percpu_usage', []))

            if cpu_delta > 0 and system_delta > 0:
                cpu_percent = (cpu_delta / system_delta) * cpu_count * 100

            return cpu_count, cpu_percent

        mem_usage, mem_limit = mem_usage()
        mem_limit = max(0.0001, mem_limit)
        cpu_count, cpu_percent = cpu_usage()
        shares = max(0.0001, self.container.attrs['HostConfig']['NanoCpus'] / 1000000000.0)
        x = {
            'id': stat['id'],
            'cpu': {
                'usage': round(cpu_percent, 2),
                'count': cpu_count,
                'shares': shares,
                'of_shares': round(cpu_percent / shares, 2)
            },
            'mem': {
                'usage': round((mem_usage * 100.0) / mem_limit, 2),
                'limit': round(mem_limit, 2),
            }
        }
        return x

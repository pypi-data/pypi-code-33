from time import sleep

import psutil
from deeputil import keeprunning
from basescript import BaseScript

def get_system_metrics():
    '''
    For keys in fields

    >>> from serverstats import get_system_metrics
    >>> fields = dict()
    >>> dl = get_system_metrics()
    >>> _fields = {'cpu': ['avg_load_5_min',
    ...                   'avg_load_15_min',
    ...                   'idle_percent',
    ...                   'iowait',
    ...                   'avg_load_1_min',
    ...                   'usage_percent'],
    ...           'disk': ['usage', 'total', 'free_percent', 'usage_percent', 'free'],
    ...           'ram': ['avail', 'usage_percent', 'avail_percent', 'usage', 'total', 'free'],
    ...           'swap': ['usage', 'total', 'free_percent', 'free', 'usage_percent']}
    >>>
    >>> for key, value in dl.iteritems():
    ...     lst = list()
    ...     if type(value) is dict and key != 'network_traffic':
    ...         for t , c in value.iteritems():
    ...             lst.append(t)
    ...         fields[key] = lst
    ...
    >>> _fields == fields
    True

    For type of every field

    >>> from flatten_dict import flatten
    >>> flat_dl = flatten(dl)
    >>> for key in flat_dl:
    ...     assert isinstance(flat_dl[key], float)

    '''
    load1, load5, load15 = psutil.os.getloadavg()
    cpu_percent = psutil.cpu_percent()
    cpu_stats = psutil.cpu_times()

    network_traffic_info = psutil.net_io_counters(pernic=True)

    memory = psutil.virtual_memory()
    swap_mem = psutil.swap_memory()

    disk = psutil.disk_usage('/')

    if swap_mem.total == 0.0:
        swapmemory_free_percent = 0.0
    else:
        swapmemory_free_percent = (swap_mem.free / swap_mem.total * 100)

    network_traffic = dict()
    for interface in network_traffic_info:
        network_traffic[interface] = {
            'sent': float(network_traffic_info[interface].bytes_sent),
            'received' : float(network_traffic_info[interface].bytes_recv),
            }

    return dict(
        #load_avg info
        cpu=dict(
            usage_percent=float(cpu_percent),
            idle_percent=float(100.00 - cpu_percent),
            iowait=float(cpu_stats.iowait),
            avg_load_15_min=float(load15),
            avg_load_5_min=float(load5),
            avg_load_1_min=float(load15),
            ),

        #ram info
        ram=dict(
            total=float(memory.total),
            avail=float(memory.available),
            usage=float(memory.used),
            free=float(memory.free),
            usage_percent=float(memory.percent),
            avail_percent=float((memory.available / memory.total * 100))
            ),

        #swap memory info
        swap=dict(
            usage_percent=float(swap_mem.percent),
            free_percent=float(swapmemory_free_percent),
            total=float(swap_mem.total),
            usage=float(swap_mem.used),
            free=float(swap_mem.free),
            ),

        #disk info
        disk=dict(
            total=float(disk.total),
            usage=float(disk.used),
            free=float(disk.free),
            usage_percent=float(disk.percent),
            free_percent=float((disk.free / disk.total * 100)),
            ),

        #network traffic
        network_traffic=network_traffic,
    )

class ServerStats(BaseScript):
    NAME = 'ServerStats'
    DESC = 'Collect important system metrics from a server and log them'

    def __init__(self):
        super(ServerStats, self).__init__()
        self.interval = self.args.interval

    def _log_exception(self, exp):
        self.log.exception('error_during_run ', exp=exp)

    @keeprunning(on_error=_log_exception)
    def _log_system_metrics(self):
        self.log.info('system_metrics', type='metric', **get_system_metrics())
        sleep(self.interval)

    def define_args(self, parser):
        parser.add_argument('-i', '--interval', type=int, default=5,
                            help='Seconds to wait after collection of stats')

    def run(self):
        self._log_system_metrics()

def main():
    ServerStats().start()

if __name__ == '__main__':
    main()

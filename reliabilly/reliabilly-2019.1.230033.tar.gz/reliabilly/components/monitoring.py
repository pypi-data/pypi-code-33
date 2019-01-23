from weakref import WeakKeyDictionary
from time import time
from urllib.parse import urlparse
from nameko.extensions import DependencyProvider
from reliabilly.components.logger import Logger
from reliabilly.settings import Constants, Settings
from reliabilly.components.tools.stats_client import StatsLogClient


def get_elapsed_milliseconds(time_start, time_end):
    return abs(round((time_end - time_start) * 1000, 1))


def monitor(monitor_name=Constants.EMPTY):
    def monitor_wrapper(func):
        def wrapper(*args, **kwargs):
            stats = StatsLogClient()
            time_start = time()
            result = func(*args, **kwargs)
            time_end = time()
            elapsed = get_elapsed_milliseconds(time_end, time_start)
            call_count_name = MonitoringProvider.get_monitor_id(Settings.SERVICE_NAME, func.__name__)
            elapsed_name = MonitoringProvider.get_monitor_id(Settings.SERVICE_NAME, func.__name__, True)
            if monitor_name:
                call_count_name = monitor_name + Constants.MONITOR_CALLS_SUFFIX
                elapsed_name = monitor_name + Constants.MONITOR_ELAPSED_SUFFIX
            # Increment the stats for function call counter
            stats.update_increment(call_count_name, Constants.MONITOR_INCR_DEFAULT)
            # Add the timing for the function call time
            stats.add_timing(elapsed_name, elapsed)
            return result
        return wrapper
    return monitor_wrapper


class MonitoringProvider(DependencyProvider):
    timestamps = WeakKeyDictionary()

    def worker_setup(self, worker_ctx):
        self.timestamps[worker_ctx] = time()

    @staticmethod
    def check_large_page(worker_ctx):
        try:
            request_url = MonitoringProvider.get_request_url(worker_ctx)
            page_size = MonitoringProvider.get_page_size_from_url(request_url)
            return page_size > Constants.DEFAULT_PAGE_SIZE
        except Exception:  # pylint: disable=broad-except
            return False

    @staticmethod
    def get_request_url(worker_ctx):
        try:
            request_url = str(worker_ctx.args).split(Constants.SPACE)[1].replace("'", '')
            return request_url
        except Exception:  # pylint: disable=broad-except
            return Constants.EMPTY

    @staticmethod
    def get_page_size_from_url(request_url):
        url_split = urlparse(request_url)
        if Constants.PAGE_SIZE in url_split.query:
            args = url_split.query.split(Constants.AMPERSAND)
            for arg in args:
                if Constants.PAGE_SIZE in arg:
                    return int(arg.split(Constants.EQUAL)[1])
        return False

    @staticmethod
    def get_monitor_id(service_name, method_name, timing=False, large=False, err=False):
        monitor_prefix = MonitoringProvider.get_monitor_prefix(service_name, method_name, err, large)
        if timing:
            return monitor_prefix + Constants.MONITOR_ELAPSED_SUFFIX
        return monitor_prefix + Constants.MONITOR_CALLS_SUFFIX

    @staticmethod
    def get_monitor_prefix(service_name, method_name, err=False, large=False):
        monitor_prefix = f'{Constants.MONITOR_PREFIX}{service_name}.{method_name}'
        if large:
            monitor_prefix += Constants.MONITOR_LARGE_KEY
        if err:
            monitor_prefix += Constants.MONITOR_ERROR_KEY
        return monitor_prefix

    def worker_result(self, worker_ctx, _=None, exc_info=None):
        large_page = self.check_large_page(worker_ctx)
        stats_client = StatsLogClient()
        service_name = worker_ctx.service_name
        method_name = worker_ctx.entrypoint.method_name
        time_end = time()
        time_start = self.timestamps.pop(worker_ctx)
        elapsed = get_elapsed_milliseconds(time_end, time_start)
        monitor_calls_id = MonitoringProvider.get_monitor_id(service_name, method_name, False, large_page, exc_info)
        monitor_elapsed_id = MonitoringProvider.get_monitor_id(service_name, method_name, True, large_page, exc_info)
        # Increment the stats for function call counter
        stats_client.update_increment(monitor_calls_id, Constants.MONITOR_INCR_DEFAULT)
        # Add the timing for the function call time
        stats_client.add_timing(monitor_elapsed_id, elapsed)

    def log_metric_for_checks(self, worker_ctx, metric_key, metric_value=Constants.EMPTY, logger=Logger(__name__)):
        request_url = self.get_request_url(worker_ctx)
        if 'infrastructure_get' in metric_key:
            logger.debug(f'Metric log for {request_url} - {metric_key}: {metric_value}')

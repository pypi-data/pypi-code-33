import json
from statsd import StatsClient
from reliabilly.settings import Settings, Constants
from reliabilly.components.tools.secret_manager import SecretManager
from reliabilly.components.web.http_requestor import HttpRequestor


def get_default_stats_client():
    return StatsClient(Settings.STATS_URL, Settings.STATS_PORT)


# noinspection PyBroadException
class StatsWebClient:  # pylint: disable=broad-except
    def __init__(self, **kwargs):
        self.web_client = kwargs.get(Constants.HTTP_CLIENT, HttpRequestor())
        self.secrets_manager = kwargs.get(Constants.SECRETS_MANAGER, SecretManager())

    def add_gauge(self, name, value, tags):
        try:
            self._send_metrics_web_request(name, value, tags)
            return True
        except Exception:
            return False

    def add_timing(self, item, time_in_ms, tags):
        try:
            self._send_metrics_web_request(item, time_in_ms, tags)
            return True
        except Exception:
            return False

    def update_increment(self, name, value, tags):
        try:
            self._send_metrics_web_request(name, value, tags)
            return True
        except Exception:
            return False

    def _send_metrics_web_request(self, name, value, tags):
        api_key = self.get_api_key()
        headers = {Constants.X_INSERT_KEY_HEADER: api_key, Constants.CONTENT_TYPE_HEADER: Constants.CONTENT_TYPE_JSON}
        payload = self.get_web_metrics_payload(name, value, tags)
        self.web_client.post(Settings.DATA_MONITORING_URL, data=payload, headers=headers)

    def get_api_key(self, local_key=Settings.LOCAL_NR_API_KEY):
        if local_key:
            return local_key
        return self.secrets_manager.get_secret(Constants.NEWRELIC_METRICS_INSERT_SECRET_ID)

    @staticmethod
    def get_web_metrics_payload(name, value, tags=None):
        metric_dictionary = {Constants.METRIC_EVENT_TYPE_KEY: Settings.METRIC_EVENT_ID,
                             Constants.METRIC_NAME_KEY: name, Constants.METRIC_VALUE_KEY: value}
        metric_dictionary.update({f'{Constants.METRIC_TAG_KEY_PREFIX}{key}': value for (key, value) in tags.items()})
        return json.dumps(metric_dictionary, default=str)


# noinspection PyBroadException
class StatsLogClient:  # pylint: disable=broad-except
    """ StatsLogClient sends metric events to metrics providers such as StatsD, Newrelic, Datadog. """
    def __init__(self, **kwargs):
        self.client = kwargs.get(Constants.CLIENT, get_default_stats_client())

    def add_gauge(self, name, value, tags=None):
        try:
            if tags:
                self.client.gauge(name, value, rate=1, delta=False, tags=tags)
                return True
            self.client.gauge(name, value, rate=1, delta=False)
            return True
        except Exception:
            return False

    def add_timing(self, item, time_in_ms):
        try:
            self.client.timing(item, time_in_ms)
            return True
        except Exception:
            return False

    def update_increment(self, name, value, tags=None):
        try:
            if tags:
                self.client.incr(name, value, tags=tags)
                return True
            self.client.incr(name, value)
            return True
        except Exception:
            return False


def monitor_collection_status(service):
    """
    Simple wrapper to collector functions that return True or False
    Sends metric data points for collection_success on True, collection_failed on False
    :param func: Function to be wrapped
    :param service: Name of the service to associate with posted data points
    :return: Wrapped function
    """
    def decorator(func):
        def wrapper(*args, **kwargs):
            result = func(*args, **kwargs)
            statsd_client = StatsLogClient()
            success_message = 'collection_success'
            failure_message = 'collection_failure'
            tags = {'service': service}
            if result:
                statsd_client.update_increment(success_message, Constants.MONITOR_INCR_DEFAULT, tags=tags)
                return result
            statsd_client.update_increment(failure_message, Constants.MONITOR_INCR_DEFAULT, tags=tags)
            return False
        return wrapper
    return decorator

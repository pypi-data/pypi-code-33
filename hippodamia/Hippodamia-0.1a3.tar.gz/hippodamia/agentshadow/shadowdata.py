import datetime
import collections


class ShadowData:
    gid = None

    properties = None
    properties_time = None

    request = {}
    request_counter = 0
    request_time = None

    config = {}
    config_counter = 0
    config_time = None

    runtime = {}
    runtime_counter = 0
    runtime_time = None

    ping = {}
    ping_counter = 0
    ping_time = None

    end = {}
    end_counter = 0
    end_time = None

    logger = None
    logger_counter = 0
    logger_time = None

    def __init__(self, gid, mongo_client):
        self.gid = str(gid)
        self.logger = collections.deque(maxlen=50)

    def process_properties(self, properties):
        self.properties = properties.export_dict()
        self.properties_time = datetime.datetime.now()

    def process_ping(self, message):
        self.ping = message
        self.ping_counter += 1
        self.ping_time = datetime.datetime.now()

    def process_config(self, message):
        self.config = message
        self.config_counter += 1
        self.config_time = datetime.datetime.now()

    def process_runtime(self, message):
        self.runtime = message
        self.runtime_counter += 1
        self.runtime_time = datetime.datetime.now()

    def process_end(self, message):
        self.end = message
        self.end_counter += 1
        self.end_time = datetime.datetime.now()

    def process_logger(self, message):
        self.logger.appendleft(message)
        self.logger_counter += 1
        self.logger_time = datetime.datetime.now()

    def process_request(self, message):
        self.request = message
        self.request_counter += 1
        self.request_time = datetime.datetime.now()

    def get_counter_dict(self):
        result = {
            "request": self.request_counter,
            "ping": self.ping_counter,
            "runtime": self.runtime_counter,
            "config": self.config_counter,
            "logger": self.logger_counter,
            "end": self.end_counter
        }
        return result

    def get_stats(self):
        return "request {}, ping {}, runtime {}, config {}, logger {}, end {}"\
            .format(self.request_counter, self.ping_counter, self.runtime_counter,
                    self.config_counter, self.logger_counter, self.end_counter)

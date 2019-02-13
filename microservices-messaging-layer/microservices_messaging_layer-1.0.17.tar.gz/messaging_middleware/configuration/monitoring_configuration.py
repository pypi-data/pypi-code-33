import os


class Monitoring:

    def __new__(cls, *args, **kwargs):
        return object.__new__(cls)

    def __init__(self):
        self.service_conf = None

    def monitoring_service(self):
        self.service_conf = {
            "monitoring": {
                "bootstrap_servers": os.environ.get('brokers', ''),
                "monitor_topic": os.environ.get('monitoring_topic', ''),
                "schema_reqistry_url": os.environ.get('schema_registry', '')
            }
        }
        return self.service_conf

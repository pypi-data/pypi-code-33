import logging as pyLogging
from google.cloud import logging as googleLogging
from google.cloud import pubsub_v1



class Logger:
    def __init__(self, app_name, logger_name, google_project_id):
        """
        Logging configuration
        :param app_name: application name
        :param logger_name: logger name
        """

        # Logger level defaults to INFO since we never had the need to change logging level until now.
        stream_format = '{app_name} %(asctime)s %(levelname)9s: %(message)s' \
            .format(app_name=app_name)

        logger = pyLogging.getLogger(logger_name)
        logger.setLevel(pyLogging.INFO)

        # All logs default to the format specified above
        log_stream_formatter = pyLogging.Formatter(stream_format)

        # Setup Google Cloud Logging and a Handler to be used by Python Default Logging
        client = googleLogging.Client(project=google_project_id)
        cloud_handler = client.get_default_handler(name=app_name)
        # Logging messages which are less severe than INFO will be ignored
        cloud_handler.setLevel(pyLogging.INFO)
        cloud_handler.setFormatter(log_stream_formatter)

        stream_handler = pyLogging.StreamHandler()
        stream_handler.setLevel(pyLogging.INFO)
        stream_handler.setFormatter(log_stream_formatter)

        # Logger which outputs to StdErr (local)
        logger.addHandler(stream_handler)
        # Logger which outputs to StackDriver
        logger.addHandler(cloud_handler)
        logger.propagate = False

        self.logger = logger
        self.app_name = app_name
        self.pubsub_client = pubsub_v1.PublisherClient()
        self.pubsub_topic = 'projects/{project}/topics/pipeline_logs'.format(project=google_project_id)
        self._push_to_pubsub = google_project_id != 'tmg-plat-dev'


    @property
    def push_to_pubsub(self):
        return self._push_to_pubsub

    @push_to_pubsub.setter
    def push_to_pubsub(self, value):
        if not isinstance(value, bool):
            raise TypeError('Value must be set to a Boolean')
        self._push_to_pubsub = value


    def info(self, message):
        self.logger.info(message)

    def warning(self, message, **attributes):
        # Publish into PubSub
        if self._push_to_pubsub:
            self.pubsub_client.publish(self.pubsub_topic, message.encode('utf-8'), pipeline=self.app_name, level='warning', **attributes)
        self.logger.warning(message)

    def error(self, message, **attributes):
        # Publish into PubSub
        if self._push_to_pubsub:
            self.pubsub_client.publish(self.pubsub_topic, message.encode('utf-8'), pipeline=self.app_name, level='error', **attributes)
        self.logger.error(message)

    def critical(self, message, **attributes):
        # Publish into PubSub
        if self._push_to_pubsub:
            self.pubsub_client.publish(self.pubsub_topic, message.encode('utf-8'), pipeline=self.app_name, level='critical', **attributes)
        self.logger.critical(message)

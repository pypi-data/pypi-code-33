import logging
import json
import datetime


def _get_log_level(level):
    """
    Convert the provided string to the corresponding logging level.

    :param level: string
    :return: logging level
    """
    if level.upper() == "CRITICAL":
        level = logging.CRITICAL
    elif level.upper() == "ERROR":
        level = logging.ERROR
    elif level.upper() == "WARNING":
        level = logging.WARNING
    elif level.upper() == "INFO":
        level = logging.INFO
    elif level.upper() == "DEBUG":
        level = logging.DEBUG
    else:
        raise ValueError("unknown value for logger level ('{}').".format(level))
    return level


class MQTTHandler:
    class _MQTTHandler(logging.StreamHandler):
        _topic = None
        _mqtt_client = None
        _gid = None
        _level = None
        _TIME_FORMAT = "%Y-%m-%dT%H:%M:%S.%fZ"  # time format string

        def __init__(self, topic, gid, level, mqtt_client):
            self._topic = topic
            self._mqtt_client = mqtt_client
            self._gid = gid
            self._level = level
            logging.StreamHandler.__init__(self)

        def emit(self, record):
            """
            {
                "gid": 1,
                "timestamp": "1985-04-12T23:20:50.520Z",
                "logger": "ZeroDivisionError: integer division or modulo by zero"
            }
            """
            msg = self.format(record)
            message = {
                "gid": self._gid,
                "timestamp": datetime.datetime.now().strftime(self._TIME_FORMAT),
                "level": self._level,
                "logger": msg
            }
            self._mqtt_client.publish(self._topic, json.dumps(message))

    _logger = None
    _handler = None

    def __init__(self, topic, level, gid, mqtt_client, logger):
        level = level.upper()
        self._logger = logger
        self._logger.info("MQTTHandler - handler init")
        self._logger.debug("MQTTHandler - level: {} / topic: {}".format(level, topic))
        self._handler = MQTTHandler._MQTTHandler(topic, gid, level, mqtt_client)
        self._handler.setLevel(_get_log_level(level))

    def start(self):
        self._logger.info("MQTTHandler - handler start")
        self._logger.addHandler(self._handler)

    def stop(self):
        self._logger.removeHandler(self._handler)
        self._logger.info("MQTTHandler - handler stop")

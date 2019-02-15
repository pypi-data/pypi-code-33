import json
import threading
import datetime
import pelops.mylogger


class Heartbeat:
    interval = None
    topic = None
    _logger = None
    _mqtt_client = None
    _stop_timer = None

    counter = 0
    last_timestamp = None

    def __init__(self, topic, interval, mqtt_client, logger):
        self.topic = topic
        self.interval = interval
        self._mqtt_client = mqtt_client
        self._logger = pelops.mylogger.get_child(logger, __class__.__name__)
        self._stop_timer = threading.Event()
        self._timer_thread = threading.Thread(target=self._timer)
        self._logger.info("__init__ done")

    def _publish(self):
        """
        {
            "heartbeat": "heartbeat",
            "timestamp": "1985-04-12T23:20:50.520Z"
        }
        """
        message = {
            "heartbeat": "heartbeat",
            "timestamp": datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S.%fZ")  # "2009-11-10T23:00:00.0Z"
        }
        self.counter += 1
        self.last_timestamp = message["timestamp"]
        self._mqtt_client.publish(self.topic, json.dumps(message))
        self._logger.info("published heartbeat ({})".format(self.counter))

    def _timer(self):
        while True:
            self._stop_timer.wait(self.interval)
            if self._stop_timer.isSet():
                break
            self._publish()

    def start(self):
        self._publish()
        self._timer_thread.start()
        self._logger.info("start finished")

    def stop(self):
        self._stop_timer.set()
        self._timer_thread.join()
        self._logger.info("stop finished")

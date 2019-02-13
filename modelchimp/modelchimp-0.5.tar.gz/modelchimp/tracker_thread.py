import time
import queue
import logging
from threading import Thread

from .event_queue import event_queue
from .enums import ClientEvent, ExperimentStatus
from .utils import current_string_datetime


class TrackerThread(Thread):
    def __init__(self, websocket_connection, key, experiment_id):
        Thread.__init__(self)
        self.stopped = False
        self.daemon = True
        self.key = key
        self.experiment_id = experiment_id
        self.web_socket = websocket_connection
        self.beat_interval = 10
        self.last_beat_snapshot = time.time()
        self.logger = logging.getLogger(__name__)

    def run(self):
        while not self.stopped:
            self.run_once()

    def run_once(self):
        try:
            if self.web_socket.is_connected():
                self.add_heart_beat()

                event = event_queue.get(10)
                self.handle_message(event)

            # Exit now if should stop
            if self.stopped:
                return
        except queue.Empty:
            pass

    def stop(self):
        self.stopped = True
        self._end()

    def handle_message(self, event):
        self.web_socket.send(event)

    def add_heart_beat(self):
        current_beat = time.time()

        if current_beat > (self.last_beat_snapshot + self.beat_interval):
            event_queue.put({
                'type' : ClientEvent.HEART_BEAT,
                'key': self.key,
                'experiment_id': self.experiment_id,
            })
            self.last_beat_snapshot = current_beat

    def update_meta_info(self, key, experiment_id):
        '''
        Update the key and experiment id
        '''
        self.web_socket.send({'type': ClientEvent.EXPERIMENT_COMPLETED,
                                'key': self.key,
                                'experiment_id': self.experiment_id,
                                'value': current_string_datetime()})
        self.key = key
        self.experiment_id = experiment_id

    def _end(self):
        self.logger.info('Experiment has ended. Closing connection with ModelChimp.')

        while True:
            try:
                if self.web_socket.is_connected():
                    event = event_queue.get_nowait()
                    self.handle_message(event)
                else:
                    break
            except queue.Empty:
                self.web_socket.send({'type': ClientEvent.EXPERIMENT_COMPLETED,
                                        'key': self.key,
                                        'experiment_id': self.experiment_id,
                                        'value': current_string_datetime()})
                break
        self.web_socket.stop()

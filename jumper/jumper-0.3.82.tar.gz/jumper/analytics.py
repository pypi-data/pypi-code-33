import sys
import Queue
import threading
import time

import requests

from __version__ import __version__


class Analytics(object):
    def __init__(self, web_api, local_jemu=False):
        self._web_api = web_api
        self._events_queue = None
        self._local_jemu = local_jemu
        self.send_intercom_events()
        self._threads = []

        if not self._local_jemu:
            self._events_queue = Queue.Queue()
            self._events_handler_should_run = True
            self._events_handler_thread = threading.Thread(target=self._event_sender)
            self._events_handler_thread.setDaemon(True)
            self._threads.append(self._events_handler_thread)
            self._events_handler_thread.start()

    def _event_sender(self):
        while True:
            try:
                event_dict = self._events_queue.get(True, timeout=0.2)
            except Queue.Empty:
                if not self._events_handler_should_run:
                    return
                else:
                    continue

            event_name = event_dict['event']
            event_labels = {}
            if "labels" in event_dict:
                event_labels = event_dict["labels"]
            event_labels['distinct_id'] = self._web_api.user_uid
            event_labels['sdk_version'] = __version__
            event_labels['Operating System'] = sys.platform

            retries = 3
            while retries > 0:
                try:
                    self._web_api.send_event(event_name, event_labels)
                except Exception:
                    retries -= 1
                    time.sleep(1)
                else:
                    break

    def send_intercom_events(self):
        try:
            head = {
                "Content-Type": "application/json",
                "Authorization": "Bearer dG9rOjg3ZTAyNzQyX2VmMjlfNDhiYV84ZTE5XzMxNzMwNzliNjcwZToxOjA="}

            event = {
                "event_name" : "Run Jumper from command line",
                "created_at": int(time.time()),
                "user_id" : self._web_api.user_uid
            }

            post_req = requests.post( 'https://api.intercom.io/events', headers=head, json=event)
            post_req.raise_for_status()

        except requests.HTTPError:
            print('SendIntercomEvent')

    def stop(self):
        self._events_handler_should_run = False
        self._stop_threads()

    def _stop_threads(self):
        for t in self._threads:
            if t.is_alive():
                t.join()

    def add_event(self, message):
        if self._events_queue:
            self._events_queue.put(message)

    def __del__(self):
        self.stop()

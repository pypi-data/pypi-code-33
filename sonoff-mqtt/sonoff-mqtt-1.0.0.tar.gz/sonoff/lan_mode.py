import json
import time
import logging

from ws4py.client.threadedclient import WebSocketClient

from .settings import API_KEY
from .device import register, unregister, handle_message

logger = logging.getLogger(__name__)


class SonoffClient(WebSocketClient):
    def __init__(self, *args, **kwargs):
        self.deviceid = None
        super().__init__(*args, **kwargs)

    def opened(self):
        timestamp = str(time.time()).replace('.', '')
        self.send(json.dumps({
            'action': 'userOnline',
            'apikey': API_KEY,
            'sequence': timestamp,
        }))

    def received_message(self, message):
        data = json.loads(message.data)
        if 'action' in data:
            response = handle_message(ws=self, **data)
            self.send(json.dumps(response))
        elif not self.deviceid:
            self.deviceid = data['deviceid']
            register(ws=self, **data)

    def closed(self, code, reason=None):
        unregister(self.deviceid)


def start_connection(host):
    ws = SonoffClient(f'ws://{host}:8081')
    ws.connect()

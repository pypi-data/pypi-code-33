from collections import defaultdict
import datetime
import json
import time
import logging

from .settings import API_KEY
from .mqtt import client

logger = logging.getLogger(__name__)
known_devices = defaultdict(lambda: {'ws': None, 'state': None})


def handle_message(*, deviceid, action, **kwargs):
    result = {
        'error': 0,
        'deviceid': deviceid,
        'apikey': API_KEY,
    }

    result.update({
        'register': register,
        'update': update,
        'query': query,
        'date': date,
    }[action](deviceid=deviceid, **kwargs))

    return result


def register(*, deviceid, ws, **kwargs):
    logger.info('Registering device %s', deviceid)
    known_devices[deviceid].update(
        ws=ws,
        state=None,
        last_seen=datetime.datetime.utcnow(),
    )
    client.register(deviceid)
    ws.send(json.dumps({
        'userAgent': 'server',
        'apikey': API_KEY,
        'deviceid': deviceid,
        'action': 'query',
        'params': ['switch']
    }))
    return {}


def update(*, deviceid, params, **kwargs):
    logger.info('Switch %s was turned %s', deviceid, params['switch'])
    known_devices[deviceid].update(
        state=params['switch'],
        last_seen=datetime.datetime.utcnow(),
    )
    client.notify(deviceid, params['switch'])
    return {}


def date(*, deviceid, **kwargs):
    return {'date': datetime.datetime.utcnow().isoformat()}


def query(*, deviceid, **kwargs):
    return {}


def unregister(deviceid):
    logger.info('Removing disconnected device %s', deviceid)
    known_devices.pop(deviceid, None)


def get_state(deviceid):
    return known_devices.get(deviceid, {}).get('state')


def set_state(deviceid, state):
    device = known_devices[deviceid]
    if state == device['state']:
        return

    logger.debug('Setting state for %s to %s', deviceid, state)

    device['state'] = state

    if device['ws']:
        device['ws'].send(json.dumps({
            'action': 'update',
            'deviceid': deviceid,
            'apikey': device.get('apikey', API_KEY),
            'selfApikey': API_KEY,
            'userAgent': 'server',
            'sequence': str(time.time()).replace('.', ''),
            'ts': 0,
            'params': {
                'switch': state
            }
        }))

    client.notify(deviceid, state)

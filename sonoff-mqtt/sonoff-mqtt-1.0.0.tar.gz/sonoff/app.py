import json
import logging

from flask import Flask, jsonify, request
from flask_sockets import Sockets

from . import converters, settings
from .device import handle_message, get_state, set_state, unregister

app = Flask('sonoff')
app.url_map.converters.update(**converters.converters)
sockets = Sockets(app)
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


@app.route('/dispatch/device', methods=['POST'])
def dispatch():
    logger.debug('Dispatching device', request.json)
    logger.info(request.get_data())
    return jsonify({
        'error': 0,
        'reason': 'ok',
        'IP': settings.SERVER_ADDRESS,
        'port': settings.SERVER_PORT,
    })


@app.route('/device/<hex:device_id>', methods=['GET', 'POST'])
def device(device_id):
    if request.method == 'GET':
        return jsonify({
            'state': get_state(device_id),
            'device_id': device_id,
        })
    elif request.method == 'POST':
        set_state(device_id, request.get_data().decode())
        return jsonify({
            'result': 'ok'
        })


@sockets.route('/api/ws')
def handler(ws):
    device_id = None
    while not ws.closed:
        # We need to listen for messages, but also provide some mechanism for
        # pushing messages.
        message = ws.receive()
        if not message:
            continue
        logger.debug('WS message received: %s', message)
        message = json.loads(message)
        if not device_id:
            device_id = message['deviceid']
        if 'action' in message:
            response = handle_message(ws=ws, **message)
            logger.debug('WS message sent: %s', response)
            ws.send(json.dumps(response))
    unregister(device_id)

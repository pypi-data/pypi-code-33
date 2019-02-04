import logging

from paho.mqtt.client import Client

logger = logging.getLogger(__name__)

ON = ['on', 'ON', True, 'True', '1', 1, b'1']


class SonoffMQTTClient(Client):
    def on_connect(self, client, userdata, flags, rc):
        client.subscribe('HomeKit/+/Lightbulb/On')
        logger.debug('Subscribed to HomeKit/+/Lightbulb/On')

    def register(self, deviceid):
        from .device import set_state

        def callback(client, userdata, message):
            state = 'on' if message.payload.decode() in ON else 'off'
            logger.info('Network says turn device %s %s', deviceid, state)
            logger.debug('Message payload %s', message.payload)
            set_state(deviceid, state)

        logger.info('Registering callback for %s', f'HomeKit/{deviceid}/Lightbulb/On')
        self.message_callback_add(f'HomeKit/{deviceid}/Lightbulb/On', callback)

    def notify(self, deviceid, state):
        logger.info('Notifying network device %s is %s', deviceid, state)
        logger.debug('Publishing %s:%s', f'HomeKit/{deviceid}/Lightbulb/On', int(state == 'on'))
        self.publish(f'HomeKit/{deviceid}/Lightbulb/On', int(state == 'on'))


client = SonoffMQTTClient()


def start():
    client.connect('mqtt.lan')
    client.loop_start()


def stop():
    client.loop_stop()

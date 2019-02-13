import json
import time
import logging

from rpicammqtt_client.loadconfig import load_config, config_file

from rpicammqtt_client import RpiCamMqttClient
from rpicammqtt_client.mqtt import MQTT

c = load_config(config_file)

numeric_level = logging.getLevelName(c['logging']['level'])
logging.basicConfig(
    filename=c['logging']['file'], filemode='w',
    level=numeric_level
)

camera = c['rpiname']
mqtt_server = c['mqtt']['server']
mqtt_port = c['mqtt']['port']
mqtt_user = c['mqtt']['user']
mqtt_pw = c['mqtt']['pw']
mqtt_qos = c['mqtt']['qos']
mqtt_keepalive = c['mqtt']['keepalive']


# Create an instance of the MQTT client based on paho mqtt and start it
MQTTC = MQTT(mqtt_server, mqtt_port, mqtt_keepalive, mqtt_user, mqtt_pw)
MQTTC.start()


# Create an instance of the rpicam client
RPI_CLIENT = RpiCamMqttClient(MQTTC.publish, MQTTC.subscribe,
                              camera, qos=1, retain=True)


def show_status(rpic):
    print("Current status: Active({}), Recording({}), Motion({})".format(
        rpic.is_active(),
        rpic.is_recording(),
        rpic.is_detecting_motion()
    ))


# Print out all current camera info
print("PanTilt views: {}".format(json.dumps(RPI_CLIENT.get_ptviews(), indent=4)))

# Watch the status and show details if it changes
curr_status = None
while True:
    time.sleep(0.5)
    new_status = RPI_CLIENT.get_status()
    if new_status != curr_status:
        curr_status = new_status
        show_status(RPI_CLIENT)


MQTTC.stop()

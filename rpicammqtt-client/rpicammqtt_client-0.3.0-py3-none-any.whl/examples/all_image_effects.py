import time
from rpicammqtt_client.loadconfig import load_config, config_file

from rpicammqtt_client import RpiCamMqttClient
from rpicammqtt_client.mqtt import MQTT

c = load_config(config_file)

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

# Loop through all effect filters and take a picture
for effect in RPI_CLIENT.EFFECTS:
    RPI_CLIENT.set_image_effect(effect)
    print(effect)
    time.sleep(10)
    RPI_CLIENT.take_picture()
    time.sleep(3)
RPI_CLIENT.set_image_effect('none')

MQTTC.stop()

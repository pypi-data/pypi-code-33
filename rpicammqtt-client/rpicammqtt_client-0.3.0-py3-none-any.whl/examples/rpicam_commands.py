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

for c in RPI_CLIENT.get_cmd_list():
    (p, d) = RPI_CLIENT.get_cmd_info(c)
    print("\n{} ({})\n{}".format(c, p, d))
print("\n")

MQTTC.stop()

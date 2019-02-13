import paho.mqtt.client as mqtt  # pylint: disable=import-error

class MQTT(object):
    """MQTT client example."""

    # pylint: disable=unused-argument

    def __init__(self, broker, port, keepalive, user, password):
        """Setup MQTT client."""
        self.topics = {}
        self._mqttc = mqtt.Client()
        self._mqttc.username_pw_set(username=user, password=password)
        self._mqttc.connect(broker, port, keepalive)

    def publish(self, topic, payload, qos, retain):
        """Publish an MQTT message."""
        self._mqttc.publish(topic, payload, qos, retain)

    def subscribe(self, topic, callback, qos):
        """Subscribe to an MQTT topic."""
        if topic in self.topics:
            return

        def _message_callback(mqttc, userdata, msg):
            """Callback added to callback list for received message."""
            callback(msg.topic, msg.payload.decode('utf-8'), msg.qos)

        self._mqttc.subscribe(topic, qos)
        self._mqttc.message_callback_add(topic, _message_callback)
        self.topics[topic] = callback

    def start(self):
        """Run the MQTT client."""
        print('Start MQTT client')
        self._mqttc.loop_start()

    def stop(self):
        """Stop the MQTT client."""
        print('Stop MQTT client')
        self._mqttc.disconnect()
        self._mqttc.loop_stop()

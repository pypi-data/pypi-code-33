from multiqq.adapters import BaseQueueAdapter
import paho.mqtt.publish as publish

class MQTTQueueAdapter(BaseQueueAdapter):

    def publish(self, channel, data, metadata=None):
        publish.single()
        pass

    def consume(self, channel, timeout=None):
        pass

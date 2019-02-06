from messaging_middleware.avro_communication_layer.Producer import Producer
from confluent_kafka import Consumer
from confluent_kafka import TopicPartition
from messaging_middleware.utils.logger import Logger
import configuration_layer.helpers.producer_messages as message
import confluent_kafka
import threading
import logging
import sys
import time
import datetime
import json


def my_assign(consumer, partitions):
    for p in partitions:
        p.offset = confluent_kafka.OFFSET_END
    consumer.assign(partitions)
    consumer.assign(list(map(lambda p: TopicPartition('tcgetconf', p), range(0, 3))))


def delivery_callback(err, msg):
    if err:
        sys.stderr.write('%% Message failed delivery: %s\n' % err)
    else:
        sys.stderr.write('%% Message delivered to %s [%d] @ %o\n' %
                         (msg.topic(), msg.partition(), msg.offset()))


class ConfigurationSeeker(threading.Thread):
    daemon = True

    def __init__(self, **kwargs):

        logging.basicConfig(
            format='%(asctime)s.%(msecs)s:%(name)s:%(thread)d:%(levelname)s:%(process)d:%(message)s',
            level=logging.INFO
        )
        logging.getLogger('urllib3.connectionpool').setLevel(logging.ERROR)

        self.service_name = kwargs.pop('service_name', None)
        self.bootstrap_servers = kwargs.pop('bootstrap_servers', None)
        self.message = kwargs.pop('message', None)
        self.key_schema = kwargs.pop('key_schema', None)
        self.schema_registry = kwargs.pop('schema_registry', None)
        self.consumer_topic = kwargs.pop('consumer_topic', None)
        self.producer_topic = kwargs.pop('producer_topic', None)
        self.security_protocol = kwargs.pop('security_protocol', 'plaintest')

        self.consumer = Consumer({'bootstrap.servers': self.bootstrap_servers,
                                  'group.id': 'configuration_seeker', 'session.timeout.ms': 6000,
                                  'enable.auto.commit': 'true',
                                  'log.connection.close':'false',
                                  'default.topic.config': {'auto.offset.reset': 'latest'},
                                  'security.protocol': self.security_protocol

                                  })

        self.consumer.assign(list(map(lambda p: TopicPartition(self.consumer_topic, p), range(0, 3))))

        self.producer = Producer(
            bootstrap_servers=self.bootstrap_servers,
            schema_reqistry_url=self.schema_registry, topic=self.producer_topic,security_protocol= self.security_protocol)

        threading.Thread.__init__(self, name='the_seeker')
        self.sleep_period = 1.0
        self.stop_event = threading.Event()
        self.configuration_directory = kwargs.pop('service_configuration_directory', 'configuration')
        self.set = kwargs.get('set',0)
        self.breakable = kwargs.get('breakable',1)
        if self.security_protocol == 'ssl':
            self.logger = Logger(ssl=1)
        else:
            self.logger = Logger()

    def stop(self):
        self.consumer.close()

    def run(self):

        try:
            while True:
                m = self.consumer.poll(1)
                "'if no messages are coming and if I haven't received a configuration, a message will be sent every 10 seconds in order to request the service configuration'"
                if m is None:
                    if self.set:
                        continue
                    self.logger.logmsg('debug', 'Requesting my configuration..', self.set)
                    ret = self.producer.produce_message(value=self.message, key=self.key_schema,
                                                        callback=delivery_callback)
                    self.logger.logmsg('info', "message sent:", ret)
                    message_to_produce = message.operation_result(service_name=self.service_name,
                                                                  last_operation='getconf',
                                                                  timestamp=datetime.datetime.now(
                                                                      datetime.timezone.utc).strftime(
                                                                      '%Y-%m-%dT%H:%M:%S%z'),
                                                                  operation_result=message.const_values()[
                                                                      'PENDING'])
                    self.logger.produce_msg(message_to_produce)

                    time.sleep(10.0)
                    continue
                if m.error() is None:
                    #self.logger.logmsg('info', 'Received message', m.value(), m.offset())
                    my_dict = m.value()
                    data_json = json.loads(my_dict.decode('ascii'))
                    "'If the receiver of the message is the same of the service name, the configuration will be saved as a JSON file. The consumer will stay active in case of updates"
                    if data_json['service_name'] == self.service_name:
                        try:
                            with open(self.configuration_directory + '/service_configuration.json', 'w') as outfile:
                                outfile.write(my_dict.decode('utf8'))
                                outfile.close()
                                message_to_produce = message.operation_result(service_name=self.service_name,
                                                                              last_operation='setconf',
                                                                              timestamp=datetime.datetime.now(
                                                                                  datetime.timezone.utc).strftime(
                                                                                  '%Y-%m-%dT%H:%M:%S%z'),
                                                                              operation_result=message.const_values()[
                                                                                  'SUCCESS']
                                                                              )
                        except ValueError as e:
                            message_to_produce = message.operation_result(service_name=self.service_name,
                                                                          last_operation='setconf',
                                                                          timestamp=datetime.datetime.now(
                                                                              datetime.timezone.utc).strftime(
                                                                              '%Y-%m-%dT%H:%M:%S%z'),
                                                                          operation_result=message.const_values()[
                                                                              'FAIL'],
                                                                          error_description=e)
                        "'notify I've just got the configuration!'"
                        self.logger.produce_msg(message_to_produce)
                        self.set = 1
                        self.logger.logmsg('debug',"is it breakable?:",self.breakable)
                        if self.breakable:
                            break

        except KeyboardInterrupt:
            sys.stderr.write('%% Aborted by user\n')
import paho.mqtt.client as mqtt
from paho.mqtt.client import MQTT_ERR_SUCCESS, MQTT_ERR_NO_CONN
from paho.mqtt.client import LOGGING_LEVEL
from threading import Event, Lock
import time
from pelops import mylogger
from collections import namedtuple
from collections import defaultdict
import queue


class StatEntry:
    """
    Counter for sent and received messages.
    """
    sent_messages = None
    received_messages = None

    def __init__(self):
        self.sent_messages = 0
        self.received_messages = 0

    def received(self):
        """increase received message counter"""
        self.received_messages += 1

    def sent(self):
        """increase sent message counter"""
        self.sent_messages += 1


class Statistics:
    """
    Holds sent/received statistics for all topics. Provides a total of received and sent messages.
    """

    def __init__(self):
        self.stats = defaultdict(StatEntry)
        self.tuple = namedtuple("Totals", ("received_messages", "sent_messages"))

    def sent(self, topic):
        """increase sent message counter for provided topic."""
        self.stats[topic].sent_messages += 1

    def recv(self, topic):
        """increase received message counter for provided topic"""
        self.stats[topic].received_messages += 1

    def get_totals(self):
        """
        sums all counter and returns a named tuple
        :return: named tuple(received_messages, sentmessages)
        """
        s = 0
        r = 0
        for stat in self.stats.values():
            s += stat.sent_messages
            r += stat.received_messages
        return self.tuple(received_messages=r, sent_messages=s)


class MyMQTTClient(object):
    """Wrapper for the paho.mqtt.client. Provides a topic to method mapping, thus enabling that one instance of
    paho.mqtt.client can be used with different incoming message handler. Further, it separates the time of
    registering a subscription from the status of the connection. Subscribed topic/handler pairs are automatically
    registered / unregistered upon connection/disconnection.

    In the configuration file you can choose to either provide an credentials file ("credentials-file") or to add
    the credentials directly ("mqtt-user", "mqtt-password").

    Topics must be provided without any wildcards.

    mqtt-client yaml configuration:
    mqtt:
        mqtt-address: localhost
        mqtt-port: 1883
        credentials-file: ~/credentials.yaml
        retain-messages: True  # optional - default FALSE
        qos: 0  # optional - default 0
        log-level: INFO  # log level for the logger

    credentials-file file:
    mqtt:
        mqtt-password: secret
        mqtt-username: user
    """

    client = None  # holds an instance of paho.mqtt.client.Client
    _config = None  # yaml configuration
    _logger = None  # logger instance
    _paho_logger = None  # child instance of _logger - for paho.client internal errors
    _quiet = None  # surpress printing high-level runtime information if set to yes.
    is_connected = None  # threading.Event - True if connection to mqtt broker has been successfully established.
    is_disconnected = None # threading.Event - True if no connection to the mqtt broker exists
    _topic_handler = None  # dict{string:list} - for each registered topic exists an entry with a list of all message handlers for this topic
    _lock_client = None  # locks processing of all relevant methods (connect, disconnect, subscribe, unsubscribe, unsubscribe all)

    _retained_messages = None  # if set to true, message broker will be signaled to retain the published messages
    _qos = None  # quality of service values for publish, subscribe, and last will
    _will_topic = None  # topic the last will should be sent ot
    _will_message = None  # message that will be used as last will

    _stats = None  # keeps statics on sent and received messages

    _unsubscribe_result = None
    _subscribe_result = None

    def __init__(self, config, logger, quiet=False):
        """
        Constructor

        :param config: config yaml structure
        :param logger: instance of logger - a child with name __name__ will be spawned
        :param quiet: boolean - if True, the runtime shell outputs like "Connecting" will be surpressed
        """

        self._config = config
        self._logger = mylogger.get_child(logger, "MQTT", config)
        self._paho_logger = mylogger.get_child(self._logger, "paho")
        self._quiet = quiet
        self._logger.info("__init__ - initalizing")
        self._logger.debug("__init__ - config: {}.".format(self._config))
        self.is_connected = Event()
        self.is_connected.clear()
        self.is_disconnected = Event()
        self.is_disconnected.set()
        self.client = mqtt.Client()
        self.client.enable_logger(self._logger)
        self._topic_handler = {}
        self._lock_client = Lock()
        self._unsubscribe_result = queue.Queue(maxsize=1)
        self._subscribe_result = queue.Queue(maxsize=1)

        try:
            self._retained_messages = self._config["retain-messages"]
        except KeyError:
            self._retained_messages = False

        try:
            self._qos = self._config["qos"]
        except KeyError:
            self._qos = 0

        self._stats = Statistics()

    def _connect_client(self):
        """Connect to mqtt broker."""
        if self.is_connected.is_set():
            self._logger.warning("_connect_client - is_connect is already set. trying to connect annyway.")
        self.client.on_connect = self._on_connect
        self.client.on_disconnect = self._on_disconnect
        self.client.on_unsubscribe = self._on_unsubscribe
        self.client.on_subscribe = self._on_subscribe
        self.client.on_message = self._on_message
        self.client.on_log = self._on_log
        self.client.username_pw_set(self._config["mqtt-user"], password=self._config["mqtt-password"])
        self.client.connect(self._config["mqtt-address"], self._config["mqtt-port"], 60)
        self.client.loop_start()
        if not self.is_connected.wait(30):
            self._logger.error("_connect_client - connection to broker could not be established.")
            raise RuntimeError("_connect_client - connection to broker could not be established.")

    def _on_subscribe(self, client, userdata, mid, granted_qos):
        self._logger.debug("_on_subscribe - client {}, userdata {}, mid {}, granted_qos {}"
                           .format(client, userdata, mid, granted_qos))
        if granted_qos != self._qos:
            self._logger.warning("_on_subscribe - requested qos {}, got qos {}".format(self._qos, granted_qos))
        self._subscribe_result.put(mid)

    def _on_unsubscribe(self, client, userdata, mid):
        self._logger.debug("_on_unsubscribe - client {}, userdata {}, mid {}"
                           .format(client, userdata, mid))
        self._unsubscribe_result.put(mid)

    def _on_log(self, client, userdata, level, buf):
        self._paho_logger.log(LOGGING_LEVEL[level], buf)

    def clear_retained_messages(self):
        """
        Signal message broker that retained messages should be cleared for all provided topics. Useful for testing.
        Connects and disconnects from broker immediately.
        """
        self._logger.info("clear_retained_messages - start")
        with self._lock_client:
            self._connect_client()
            for topic in self._topic_handler.keys():
                self._logger.info("clear_retained_messages() - clearing topic '{}'.".format(topic))
                self.publish(topic, None)  # publishing a message with zero bytes clears retained value
        self.disconnect()
        self._logger.info("clear_retained_messages - done")

    def connect(self):
        """Connect to the mqtt broker using the provided configuration and registering of all provided message
        handler."""

        if not self._quiet:
            print("MyMQTTClient.connect() - Connecting to mqtt.")
        self._logger.info("connect() - Connecting to mqtt.")
        with self._lock_client:
            self._connect_client()
            self._publish_will()
            for topic in self._topic_handler.keys():
                self._logger.info("connect() - subscribe to topic '{}'.".format(topic))
                self._execute_subscribe(topic)

        self._logger.info("connect() - connected.")

    def disconnect(self):
        """Disconnect from mqtt broker and set is_connected to False."""
        if not self._quiet:
            print("MyMQTTClient.disconnect() - disconnecting from mqtt")
        self._logger.info("disconnect() - disconnecting from mqtt")
        with self._lock_client:
            self.client.disconnect()
            if not self.is_disconnected.wait(30):
                self._logger.error("disconnect - connection to broker could not be closed.")
                raise RuntimeError("disconnect - connection to broker could not be closed.")
        self._logger.info("disconnect() - disconnected.")

    def _on_disconnect(self, client, userdata, rc):
        """
        Return code after trying to connect to mqtt broker. If successfully connect, is_disconnected is True.
        Params as defined by paho.mqtt.client. Sets is_disconnected and claers is_disconnected events.

        # The rc parameter indicates the disconnection state. If MQTT_ERR_SUCCESS (0), the callback was called in
        # response to a disconnect() call. If any other value the disconnection was unexpected, such as might be
        # caused by a network error.
        """
        self.is_connected.clear()
        self.is_disconnected.set()

        if rc == 0:
            if not self._quiet:
                print("MyMQTTClient._on_disconnect - disconnected.")
            self._logger.info("_on_disconnect - disconnected.")
        else:
            if not self._quiet:
                print("MyMQTTClient._on_disconnect - unexpected disconnection.")
            self._logger.warning("_on_disconnect - unexpected disconnection.")

    def _on_connect(self, client, userdata, flags, rc):
        """
        Return code after trying to connect to mqtt broker. If successfully connected, is_connected is True. Params as
        defined by paho.mqtt.client. Sets is_connected and clears is_disconnected events. Raises runtime error if
        result code is != 0.

        # 0: Connection successful
        # 1: Connection refused - incorrect protocol version
        # 2: Connection refused - invalid client identifier
        # 3: Connection refused - server unavailable
        # 4: Connection refused - bad username or password
        # 5: Connection refused - not authorised
        # 6-255: Currently unused.
        """
        if rc == 0:
            self.is_connected.set()
            self.is_disconnected.clear()
            if not self._quiet:
                print("MyMQTTClient._on_connect - Connected with result code " + str(rc))
            self._logger.info("_on_connect - Connected with result code " + str(rc))
        else:
            if rc == 1:
                msg = "result code 1: Connection refused - incorrect protocol version"
            elif rc == 2:
                msg = "result code 2: Connection refused - invalid client identifier"
            elif rc == 3:
                msg = "result code 3: Connection refused - server unavailable"
            elif rc == 4:
                msg = "result code 4: Connection refused - bad username or password"
            elif rc == 5:
                msg = "result code 5: Connection refused - not authorised"
            else:
                msg = "result code {}: Currently unused.".format(rc)
            if not self._quiet:
                print("MyMQTTClient._on_connect - Failed! " + msg)
            self._logger.error("_on_connect - Failed! " + msg)
            raise RuntimeError("_on_connect - Failed! " + msg)

    def _on_message(self, client, userdata, msg):
        """on message handler as defined by paho.mqtt.client. calls every for this topic registered handler with
        the message payload."""
        t = time.time()

        self._logger.info("_on_message - received message '{}' on topic '{}' @{}s. {}".
                  format(msg.payload, msg.topic, t, msg))
        self._stats.recv(msg.topic)

        for handler in self._topic_handler[msg.topic]:
            self._logger.info("_on_message - calling handler '{}' ({}).".format(handler, t))
            try:
                handler(msg.payload)
            except (KeyboardInterrupt, SystemExit):
                raise
            except Exception as err:
                self._logger.exception(err)
                raise err

    def publish(self, topic, msg):
        """
        simple wrapper for paho.mqtt.client publish. publishes message if connected; raises RuntimeWarning
        otherwise.

        :param topic: string - mqtt topic
        :param msg: payload
        """
        self._logger.info("publish - publishing to topic '{}' the message '{}'.".format(topic, msg))
        if self.is_connected.is_set():
            self.client.publish(topic, msg, qos=self._qos, retain=self._retained_messages)
            self._stats.sent(topic)
        else:
            self._logger.warning("publish - trying to publish while not being connected to mqtt broker.")
            raise RuntimeWarning("publish - trying to publish while not being connected to mqtt broker.")

    def _publish_will(self):
        """simple wrapper for paho.mqtt.client set_will. publishes will if connected; raises RuntimeWarning
        otherwise."""
        if self._will_message is None or self._will_topic is None:
            self._logger.info("_publish_will - no will provided")
        else:
            self._logger.info("_publish_will - publishing last will")
            if self.is_connected.is_set():
                self.client.will_set(self._will_topic, self._will_message, qos=self._qos, retain=self._retained_messages)
            else:
                self._logger.warning("_publish_will - trying to publish while not being connected to mqtt broker.")
                raise RuntimeWarning("_publish_will - trying to publish while not being connected to mqtt broker.")

    def set_will(self, topic, will):
        """
        Set will parameters. If already connected, it will be published immediately or stored to be published upon
        connection.

        :param topic: string - mqtt topic
        :param will: payload
        """
        self._logger.info("set_will - setting last will to topic '{}' and message '{}'."
                          .format(topic, will))

        if topic is None:
            self._logger.error("set_will - topic ({}) must be not None.".format(topic))
            raise ValueError("set_will - topic ({}) must be not None.".format(topic))

        self._will_topic = topic
        self._will_message = will
        if self.is_connected.is_set():
            self._publish_will()

    def subscribe(self, topic, handler, ignore_duplicate=False):
        """
        Registeres the provided handler to the provided topic. The handler is expected to accept the message payload
        as only parameter (e.g. "def myhandler(message)", "mymqttclient.subscribe('/topic', myhandler)"). For each topic
        several handler can be registered. If a topic/handler pair is suscribed more than once a ValueError will be
        raised.

        :param topic: string - mqtt topic
        :param handler: method
        :param ignore_duplicate: no error will be produce in case of topic/handler pair has already been added
        """
        self._logger.info("subscribe - subscribing topic '{}' with handler '{}'.".format(topic, handler))
        with self._lock_client:
            try:
                h = self._topic_handler[topic]
                h.append(handler)
                if h.count(handler) > 1:
                    if not ignore_duplicate:
                        self._logger.error("subscribe - topic/handler pair already added. ({}/{})".
                                         format(topic, handler))
                        raise ValueError("subscribe - topic/handler pair already added. ({}/{})".
                                         format(topic, handler))
            except KeyError:
                self._topic_handler[topic] = [handler,]
            if self.is_connected.is_set():
                self._logger.info("subscribe - activating topic subscription.")
                self._execute_subscribe(topic)

    def unsubscribe(self, topic, handler, ignore_not_found=False):
        """
        Unsubscribe topic/handler pair (reverse of subscribe). As several handler might be registered for the same topic
        and the same client might be used in different microservices, removing all handler for a given topic might
        result in unwanted side effects.

        :param topic: string - mqtt topic
        :param handler: method
        :param ignore_not_found: no error will be produce in case of topic/handler pair does not exist
        """

        self._logger.info("unsubscribe - unsubscribing topic '{}' with handler '{}'.".
                          format(topic, handler))
        with self._lock_client:
            try:
                if len(self._topic_handler[topic]) > 1:
                    self._logger.debug("unsubscribe - more than one handler registered for topic.")
                    if handler not in self._topic_handler[topic]:
                        if not ignore_not_found:
                            self._logger.error("unsubscribe - unknown handler '{}' for topic '{}'"
                                                 .format(handler, topic))
                            raise ValueError("unsubscribe - unknown handler '{}' for topic '{}'"
                                             .format(handler, topic))

                    self._topic_handler[topic].remove(handler)
                else:
                    self._logger.debug("unsubscribe - clear topic handler entry from dict and unsubscribe from "
                                       "topic.")
                    if handler not in self._topic_handler[topic]:
                        if not ignore_not_found:
                            self._logger.error("unsubscribe - unknown handler '{}' for topic '{}'"
                                                 .format(handler, topic))
                            raise ValueError("unsubscribe - unknown handler '{}' for topic '{}'"
                                             .format(handler, topic))

                    del(self._topic_handler[topic])
                    self._execute_unsubscribe(topic)

            except KeyError:
                if not ignore_not_found:
                    self._logger.error("unsubscribe - unknown topic '{}'".format(topic))
                    raise

    def unsubscribe_all(self):
        """
        Reset all subscriptions. Mainly used for testing purposes.
        """
        self._logger.info("unsubscribe_all")
        with self._lock_client:
            for topic in self._topic_handler:
                self._logger.info("unsubscribe_all - topic '{}'".format(topic))
                self._execute_unsubscribe(topic)
            self._topic_handler.clear()

    def _execute_unsubscribe(self, topic):
        self._execute("_execute_unsubscribe", self.client.unsubscribe, self._unsubscribe_result, topic)

    def _execute_subscribe(self, topic):
        self._logger.debug("_execute_subscribe - start {}".format(topic))
        self._execute("_execute_subscribe", self.client.subscribe, self._subscribe_result, topic, qos=self._qos)
        self._logger.debug("_execute_subscribe - end {}".format(topic))

    def _execute(self, caller_name, method, q, *args, **kwargs):
        self._logger.info("{} - executing".format(caller_name))
        self._logger.debug("__execute: caller_name {}, method {}, q {}, args {}, kwargs {}"
                           .format(caller_name, method, q, args, kwargs))
        try:
            result, mid = method(*args, **kwargs)
        except:
            err = "{} - unknown error".format(caller_name)
            self._logger.error(err)
            raise err

        if result != MQTT_ERR_SUCCESS:
            if result == MQTT_ERR_NO_CONN:
                err = "{} - MQTT_ERR_NO_CONN".format(caller_name)
            else:
                err = "{} - unknown error {}".format(caller_name, result)
            raise RuntimeError(err)

        try:
            self._logger.info("{} - waiting for ACK".format(caller_name))
            result_mid = q.get(timeout=10)
        except queue.Empty as err:
            self._logger.error("{} - {}".format(caller_name, err))
            raise err

        if mid != result_mid:
            err = "{} - expected mid {}, got mid {}".format(caller_name, mid, result_mid)
            self._logger.error(err)
            raise RuntimeError(err)

        self._logger.info("{} - success".format(caller_name))

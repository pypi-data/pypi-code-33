from mqtt.mqtt_core import MqttCore as MqttClient
from core.internals.DefaultProcessor import DefaultProcessor
from mqtt.util.providers import EndpointProvider
from mqtt.util.providers import CertificateCredentialsProvider
from core.internals.SubTopicCache import SubTopicCache
from concurrent.futures import wait
from core.exception.EnvisionException import EnvisionException

DROP_OLDEST = 0
DROP_NEWEST = 1

class MqttConnection(object):

    profile = None
    transport = None
    def __init__(self, profile):
        self.profile = profile
        self._newMqttClient()
        self.subTopicCache = SubTopicCache()
        self.mqttProcessor = DefaultProcessor(self.transport, self.profile, self.subTopicCache)

    def _newMqttClient(self):
        regionUrl = self.profile.getRegionURL()
        regions = regionUrl.split(':')
        self.protocol = ''
        self.host = ''
        self.port = ''
        if len(regions) == 3:
            self.protocol = regions[0]
            self.host = regions[1].replace('//', '')
            self.port = regions[2]
        else:
            raise EnvisionException('RegionURL can not empty.')
        if self.protocol.lower() == 'websockets':
            self.profile.setUserWebSocket(True)
            self.transport = MqttClient(self.profile.getClientId(), False, self.profile.MQTTv3_1_1, True)
        else:
            self.transport = MqttClient(self.profile.getClientId(), False, self.profile.MQTTv3_1_1, False)

    def _createConnectionOptions(self):
        if self.profile.getSSLSecured():
            if self.profile.getUseWebSocket():
                self._configureCredentials(self.profile.getSSLRootCAPath())
            else:
                self._configureCredentials(self.profile.getSSLRootCAPath(),
                                           self.profile.getSSLPrivateKeyPath(),
                                           self.profile.getSSLCertificatePath(),
                                           self.profile.getSSLPrivateKeyPass())
        self._configureEndpoint(self.host, self.port)
        self._configureConnectDisconnectTimeout(self.profile.getConnectionTimeout())
        self._configureMQTTOperationTimeout(self.profile.getTimeToWait())
        self._configureUsernamePassword(self.profile.getMqttUser(), self.profile.getMqttPassword())

    def connect(self, callback=None):
        try:
            self._createConnectionOptions()
            if callback is not None:
                self.mqttProcessor.setConnectCallback(callback)
                self._connect(self.profile.getKeepAlive())
            else:
                self._connectAsync(self.profile.getKeepAlive(), callback)
        except Exception as e:
            raise EnvisionException(e.message)

    def disconnect(self, callback=None):
        try:
            if callback is not None:
                self.mqttProcessor.setDisconnectCallback(callback)
                self._disconnect()
            else:
                self._disconnectAsync(callback)
        except Exception as e:
            raise EnvisionException(e.message)

    def fastPublish(self, request):
        try:
            self.mqttProcessor.doFastPublish(request)
        except Exception as e:
            raise EnvisionException(e.message)

    def publish(self, request, callback=None):
        try:
            topic = request.getAnswerTopic()
            if not self.subTopicCache.exists(topic):
                self.transport.subscribe(topic, request.getQos())
                self.subTopicCache.put(topic)

            if callback is not None:
                self.mqttProcessor.createCallbackTask(request, callback, self.profile.getTimeToWait())
            else:
                futureTask = self.mqttProcessor.createFutureTask(request)
                wait([futureTask], self.profile.getTimeToWait())
                if futureTask.done():
                    return futureTask.result()
        except Exception as e:
            raise EnvisionException(e.message)

    def getClientId(self):
        return self.profile.getClientId()

    def close(self):
        pass

    def getProcessor(self):
        return self.mqttProcessor

    def isConnected(self):
        pass

    def onOnline(self):
        pass

    def onOffline(self):
        self.mqttProcessor.onConnectFailed()

    def onMessage(self, message):
        self.mqttProcessor.messageArrived(message)

    def _connect(self, keepAliveIntervalSecond=60):
        self._load_callbacks()
        return self.transport.connect(keepAliveIntervalSecond)

    def _connectAsync(self, keepAliveIntervalSecond=60, ackCallback=None):
        self._load_callbacks()
        return self.transport.connect_async(keepAliveIntervalSecond, ackCallback)

    def _load_callbacks(self):
        self.transport.on_online = self.onOnline
        self.transport.on_offline = self.onOffline
        self.transport.on_message = self.onMessage

    def _disconnect(self):
        return self.transport.disconnect()

    def _disconnectAsync(self, ackCallback=None):
        return self.transport.disconnect_async(ackCallback)

    def _publish(self, topic, payload, QoS):
        return self.transport.publish(topic, payload, QoS, False)

    def _publishAsync(self, topic, payload, QoS, ackCallback=None):
        return self.transport.publish_async(topic, payload, QoS, False, ackCallback)

    def _subscribe(self, topic, QoS, callback):
        return self.transport.subscribe(topic, QoS, callback)

    def _subscribeAsync(self, topic, QoS, ackCallback=None, messageCallback=None):
        return self.transport.subscribe_async(topic, QoS, ackCallback, messageCallback)

    def _unsubscribe(self, topic):
        return self.transport.unsubscribe(topic)

    def _unsubscribeAsync(self, topic, ackCallback=None):
        return self.transport.unsubscribe_async(topic, ackCallback)

    def _configureEndpoint(self, host, port):
        endpoint_provider = EndpointProvider()
        endpoint_provider.set_host(host)
        endpoint_provider.set_port(port)
        self.transport.configure_endpoint(endpoint_provider)

    def _configureCredentials(self, CAFilePath, KeyPath='', CertificatePath='', keyPass = None):
        cert_credentials_provider = CertificateCredentialsProvider()
        cert_credentials_provider.set_ca_path(CAFilePath)
        cert_credentials_provider.set_key_path(KeyPath)
        cert_credentials_provider.set_cert_path(CertificatePath)
        cert_credentials_provider.set_key_pass(keyPass)
        self.transport.configure_cert_credentials(cert_credentials_provider)

    def _configureLastWill(self, topic, payload, QoS, retain=False):
        self.transport.configure_last_will(topic, payload, QoS, retain)

    def _clearLastWill(self):
        self.transport.clear_last_will()

    # def _configureAutoReconnectBackoffTime(self, baseReconnectQuietTimeSecond, maxReconnectQuietTimeSecond,
    #                                       stableConnectionTimeSecond):
    #     self.transport.configure_reconnect_back_off(baseReconnectQuietTimeSecond, maxReconnectQuietTimeSecond,
    #                                                  stableConnectionTimeSecond)

    def _configureOfflinePublishQueueing(self, queueSize, dropBehavior=DROP_NEWEST):
        self.transport.configure_offline_requests_queue(queueSize, dropBehavior)

    def _configureDrainingFrequency(self, frequencyInHz):
        self.transport.configure_draining_interval_sec(1 / float(frequencyInHz))

    def _configureConnectDisconnectTimeout(self, timeoutSecond):
        self.transport.configure_connect_disconnect_timeout_sec(timeoutSecond)

    def _configureMQTTOperationTimeout(self, timeoutSecond):
        self.transport.configure_operation_timeout_sec(timeoutSecond)

    def _configureUsernamePassword(self, username, password=None):
        self.transport.configure_username_password(username, password)

    def _enableMetricsCollection(self):
        self.transport.enable_metrics_collection()

    def _disableMetricsCollection(self):
        self.transport.disable_metrics_collection()
import datetime
from hippodamia.enums import Enforcement
import json
import pelops.mylogger


class Onboarding:
    _logger = None
    _mqtt_client = None
    _agentshadows = None
    _asfactory = None

    enforcement = None
    protocol_version = None
    topic_onboarding_request = None
    counter = 0
    gid_list = set()
    last_timestamp = None
    last_message = None

    def __init__(self, protocol_version, topic_onboarding_request, enforcement, agentshadows, asfactory, mqtt_client, logger):
        self.protocol_version = protocol_version
        self._logger = pelops.mylogger.get_child(logger, __class__.__name__)
        self._mqtt_client = mqtt_client
        self.enforcement = enforcement
        self._agentshadows = agentshadows
        self._asfactory = asfactory
        self.topic_onboarding_request = topic_onboarding_request
        self._logger.info("__init__ done")

    def start(self):
        self._mqtt_client.subscribe(self.topic_onboarding_request, self._handler_onboarding_request)
        self._logger.info("subscribed to {}".format(self.topic_onboarding_request))

    def stop(self):
        self._mqtt_client.unsubscribe(self.topic_onboarding_request, self._handler_onboarding_request)
        self._logger.info("unsubscribed from {}".format(self.topic_onboarding_request))

    def _handler_onboarding_request(self, message):
        """
        {
            "uuid": "550e8400-e29b-11d4-a716-446655440000",
            "onboarding-topic": "/hippodamia/550e8400-e29b-11d4-a716-446655440000",
            "protocol-version": 1,
            "timestamp": "1985-04-12T23:20:50.520Z",
            "identifier": {
                "gid": 1,
                "type": "copreus",
                "name": "display-driver",
                "location": "flat",
                "room": "living room",
                "device": "thermostat",
                "decription": "lorem ipsum",
                "host-name": "rpi",
                "node-id": "00-07-E9-AB-CD-EF",
                "ips": [
                    "192.168.0.1",
                    "10.0.1.2",
                    "2001:0db8:85a3:08d3:1319:8a2e:0370:7344"
                ],
                "config-hash": "cf23df2207d99a74fbe169e3eba035e633b65d94"
            }
        }
        """
        message = message.decode("utf8")
        message = json.loads(message)
        self.last_message = message
        self._logger.info("_handler_onboarding_request - received request")
        self._logger.debug("_handler_onboarding_request - message: {}".format(message))

        self.counter += 1
        self.last_timestamp = datetime.datetime.now()

        if message["protocol-version"] != self.protocol_version:
            message = "handler_onboarding_request - expected protocol version {}, message: {}"\
                .format(self.protocol_version, message)
            self._logger.error(message)
        else:
            identifier = message["identifier"]
            self._logger.debug("_handler_onboarding_request - identifier: {}".format(identifier))
            gid = str(identifier["gid"])
            self.gid_list.add(gid)
            self._logger.debug("_handler_onboarding_request - gid: {}".format(gid))

            shadow = None
            if gid not in self._agentshadows:
                self._logger.debug("_handler_onboarding_request - unknown gid")
                if self.enforcement == Enforcement.NONE:
                    self._logger.debug("_handler_onboarding_request - Enforcement.NONE")
                    shadow = self._asfactory.new_agentshadow(gid=gid)
                    shadow.start()
                elif self.enforcement == Enforcement.IGNORE:
                    self._logger.debug("_handler_onboarding_request - Enforcement.IGNORE")
                    return
                elif self.enforcement == Enforcement.STRICT:
                    self._logger.debug("_handler_onboarding_request - Enforcement.STRICT")
                    self._logger.error("handler_onboarding_request - required is set to strict and incoming is gid "
                                       "not pre-configured. '{}'".format(message))
                    return
                else:
                    message = "handler_onboarding_request - dont know how to handler required '{}'"\
                        .format(self.enforcement)
                    self._logger.error(message)
                    raise ValueError(message)
            else:
                self._logger.debug("_handler_onboarding_request - existing gid {}".format(gid))
                shadow = self._agentshadows[gid]

            self._logger.debug("_handler_onboarding_request - {}".format(shadow))
            shadow.process_onboarding_request(message)

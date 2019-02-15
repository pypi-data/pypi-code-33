import json
from hippodamia.agentshadow.properties import Properties
import hippodamia.agentshadow.states.state_machine
import pelops.mylogger
from hippodamia.enums import Necessity
from hippodamia.agentshadow.states.event_ids import event_ids
from hippodamia.agentshadow.states.state_ids import state_ids
from hippodamia.agentshadow.shadowdata import ShadowData


class AgentShadow:
    _mqtt_client = None
    _logger = None
    _update_available = None

    _state_machine = None

    _basic_topics = None

    timings = None
    activity_topics = None
    shadow_data = None
    properties = None
    states = None

    def __init__(self, topics, timings, update_available, mongo_client, mqtt_client, logger, preload_config=None, gid=None):
        self._mqtt_client = mqtt_client
        self._logger = pelops.mylogger.get_child(logger, "AgentShadow")
        self._basic_topics = topics
        self.timings = timings
        self._update_available = update_available

        self.properties = Properties(self._logger)

        if gid:
            self._logger.info("__init__ - setting gid")
            self.properties.gid = str(gid)
            self.properties.necessity = Necessity.SPONTANEOUS
        elif preload_config:
            self._process_preload_config(preload_config)
        else:
            self._logger.error("__init__ - preload_config and gid are None")
            raise ValueError("__init__ - preload_config and gid are None")

        if self.properties.gid is None:
            self._logger.error("__init__ - gid is None")
            raise ValueError("__init__ - gid is None")
        else:
            self._logger = pelops.mylogger.get_child(logger, str(self.properties.gid))

        self._set_basic_topics()
        self._init_state_machine()

        self.shadow_data = ShadowData(str(self.properties.gid), mongo_client)
        self.shadow_data.process_properties(self.properties)

    def get_state_id(self):
        return self._state_machine.get_active_state().id

    def set_health(self, health):
        self.properties.health = health
        self._logger.debug("set_health to {}".format(self.properties.health.name))

    def _set_basic_topics(self):
        self.activity_topics = {}
        activity_base = self._basic_topics["activity-base"]
        if activity_base[-1] == "/":
            activity_base = activity_base[:-1]
        self.activity_topics["ping"] = "{}/{}/ping".format(activity_base, self.properties.gid)
        self.activity_topics["runtime"] = "{}/{}/runtime".format(activity_base, self.properties.gid)
        self.activity_topics["config"] = "{}/{}/config".format(activity_base, self.properties.gid)
        self.activity_topics["end"] = "{}/{}/end".format(activity_base, self.properties.gid)
        self.activity_topics["logger"] = "{}/{}/logger".format(activity_base, self.properties.gid)

    def _process_preload_config(self, preload_config):
        self._logger.info("_process_preload_config - start")
        self._logger.debug("_process_preload_config: {}".format(preload_config))

        if "gid" in preload_config:
            self.properties.gid = str(preload_config["gid"])
        if "name" in preload_config:
            self.properties.name = preload_config["name"]
        if "location" in preload_config:
            self.properties.location = preload_config["location"]
        if "room" in preload_config:
            self.properties.room = preload_config["room"]
        if "device" in preload_config:
            self.properties.device = preload_config["device"]
        if "necessity" in preload_config:
            necessity = Necessity.get_enum(preload_config["necessity"])
            if necessity != Necessity.OPTIONAL and necessity != Necessity.REQUIRED:
                msg = "_process_preload_config - unexpected value '{}' for necessity. must " \
                      "be 'required' or 'optional'.",format(preload_config["necessity"])
                self._logger.error(msg)
                raise ValueError(msg)
            self.properties.necessity = necessity
        self._logger.info("_process_preload_config - finished")

    def _init_state_machine(self):
        self._state_machine, self.states = hippodamia.agentshadow.states.\
            state_machine.create(self._update_available, self.timings, self.set_health, self._logger)
        self.states[state_ids.ONBOARDING].func_send_onboarding_response = self._send_onboarding_response
        self.states[state_ids.ONBOARDING].func_deactivate_recv_messages = self.deactivate_recv_messages
        self.states[state_ids.ONBOARDING].func_activate_recv_messages = self.activate_recv_messages
        self.states[state_ids.STOPPED].func_deactivate_recv_messages = self.deactivate_recv_messages

    def start(self):
        self._state_machine.firststart()

    def stop(self):
        try:
            # trying to initiate offboarding no matter what the current state is
            self._state_machine.asyncoperate(event_ids.OFFBOARDING)
        except KeyError:
            pass  # not every every state has a link to offboarding
        self._state_machine.stop()

    def process_onboarding_request(self, message):
        """
        {
          "uuid": "550e8400-e29b-11d4-a716-446655440000",
          "onboarding-topic": "/hippodamia/550e8400-e29b-11d4-a716-446655440000",
          "protocol-version": 1,
          "timestamp": "1985-04-12T23:20:50.520Z",
          "identifier": {
            "gid": 1,
            "type": "copreus",
            "version": "0.3.1",
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
        self._logger.info("process_onboarding_request - start")
        self._logger.debug("process_onboarding_request - message: {}".format(message))

        self.properties.uuid = message["uuid"]
        self.properties.onboarding_topic = message["onboarding-topic"]
        self.properties.protocol_version = message["protocol-version"]

        self.properties.gid = str(message["identifier"]["gid"])
        self.properties.location = message["identifier"]["location"]
        self.properties.room = message["identifier"]["room"]
        self.properties.device = message["identifier"]["device"]

        self.properties.type = message["identifier"]["type"]
        self.properties.version = message["identifier"]["version"]
        self.properties.name = message["identifier"]["name"]
        self.properties.description = message["identifier"]["description"]
        self.properties.host_name = message["identifier"]["host-name"]
        self.properties.node_id = message["identifier"]["node-id"]
        self.properties.ips = message["identifier"]["ips"]
        self.properties.config_hash = message["identifier"]["config-hash"]

        self.shadow_data.process_request(message)
        self.shadow_data.process_properties(self.properties)

        self._logger.info("process_onboarding_request - finished")

        self._state_machine.asyncoperate(event_ids.ONBOARDING_REQUEST)
        
    def _send_onboarding_response(self):
        """
        {
            "uuid": "550e8400-e29b-11d4-a716-446655440000",
            "gid": 1,
            "topics-activity": {
                "ping": "/hippodamia/commands",
                "runtime": "/hippodamia/commands",
                "config": "/hippodamia/commands",
                "end": "/hippodamia/commands",
                "logger": "/hippodamia/commands"
            },
            "topics-commands": {
                "end": "/hippodamia/commands",
                "reonboarding": "/hippodamia/commands",
                "ping_on_request": "/hippodamia/commands",
                "config_on_request": "/hippodamia/commands",
                "runtime_on_request": "/hippodamia/commands",
                "heartbeat": "/hippodamia/commands"
            }
        }
        """
        message = {
            "uuid": self.properties.uuid,
            "gid": self.properties.gid,
            "topics-activity": {
                "ping": self.activity_topics["ping"],
                "runtime": self.activity_topics["runtime"],
                "config": self.activity_topics["config"],
                "end": self.activity_topics["end"],
                "logger": self.activity_topics["logger"],
            },
            "topics-commands": {
                "end": self._basic_topics["command-end"],
                "reonboarding": self._basic_topics["command-reonboarding"],
                "ping_on_request": self._basic_topics["command-ping-on-request"],
                "config_on_request": self._basic_topics["command-config-on-request"],
                "runtime_on_request": self._basic_topics["command-runtime-on-request"],
                "heartbeat": self._basic_topics["heartbeat"],
            }
        }
        message = json.dumps(message)
        self._logger.debug("_send_onboarding_response - topic: {}, message: {}"
                           .format(self.properties.onboarding_topic, message))
        self._logger.debug(self.properties.export_dict())
        self._mqtt_client.publish(self.properties.onboarding_topic, message)

    def activate_recv_messages(self):
        self._logger.info("activate_recv_messages")

        self._logger.debug("activate_recv_messages - topic ping {}".format(self.activity_topics["ping"]))
        self._mqtt_client.subscribe(self.activity_topics["ping"], self._handler_ping, ignore_duplicate=True)

        self._logger.debug("activate_recv_messages - topic runtime {}".format(self.activity_topics["runtime"]))
        self._mqtt_client.subscribe(self.activity_topics["runtime"], self._handler_runtime, ignore_duplicate=True)

        self._logger.debug("activate_recv_messages - topic config {}".format(self.activity_topics["config"]))
        self._mqtt_client.subscribe(self.activity_topics["config"], self._handler_config, ignore_duplicate=True)

        self._logger.debug("activate_recv_messages - topic end {}".format(self.activity_topics["end"]))
        self._mqtt_client.subscribe(self.activity_topics["end"], self._handler_end, ignore_duplicate=True)

        self._logger.debug("activate_recv_messages - topic logger {}".format(self.activity_topics["logger"]))
        self._mqtt_client.subscribe(self.activity_topics["logger"], self._handler_logger, ignore_duplicate=True)

    def deactivate_recv_messages(self):
        self._logger.info("deactivate_recv_messages")

        self._logger.debug("activate_recv_messages - topic ping {}".format(self.activity_topics["ping"]))
        self._mqtt_client.unsubscribe(self.activity_topics["ping"], self._handler_ping, ignore_not_found=True)

        self._logger.debug("activate_recv_messages - topic runtime {}".format(self.activity_topics["runtime"]))
        self._mqtt_client.unsubscribe(self.activity_topics["runtime"], self._handler_runtime, ignore_not_found=True)

        self._logger.debug("activate_recv_messages - topic config {}".format(self.activity_topics["config"]))
        self._mqtt_client.unsubscribe(self.activity_topics["config"], self._handler_config, ignore_not_found=True)

        self._logger.debug("activate_recv_messages - topic end {}".format(self.activity_topics["end"]))
        self._mqtt_client.unsubscribe(self.activity_topics["end"], self._handler_end, ignore_not_found=True)

        self._logger.debug("activate_recv_messages - topic logger {}".format(self.activity_topics["logger"]))
        self._mqtt_client.unsubscribe(self.activity_topics["logger"], self._handler_logger, ignore_not_found=True)

    def _handler_ping(self, message):
        self._logger.info("_handler_ping - received ping")
        message = json.loads(message.decode("utf8"))
        self.shadow_data.process_ping(message)
        self._state_machine.asyncoperate(event_ids.REGULAR_MESSAGE)

    def _handler_runtime(self, message):
        self._logger.info("_handler_runtime - received runtime")
        message = json.loads(message.decode("utf8"))
        self.shadow_data.process_runtime(message)
        self._state_machine.asyncoperate(event_ids.REGULAR_MESSAGE)

    def _handler_config(self, message):
        self._logger.info("_handler_config - received config")
        message = json.loads(message.decode("utf8"))
        self.shadow_data.process_config(message)
        self._state_machine.asyncoperate(event_ids.REGULAR_MESSAGE)

    def _handler_end(self, message):
        self._logger.info("_handler_end - received end")
        message = json.loads(message.decode("utf8"))
        self.shadow_data.process_end(message)
        self._state_machine.asyncoperate(event_ids.OFFBOARDING)

    def _handler_logger(self, message):
        self._logger.info("_handler_logger - received logger")
        message = json.loads(message.decode("utf8"))
        self.shadow_data.process_logger(message)
        self._state_machine.asyncoperate(event_ids.REGULAR_MESSAGE)

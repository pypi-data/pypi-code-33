import threading
import json

from pelops.abstractmicroservice import AbstractMicroservice
import hippodamia
from hippodamia.agentshadow.agentshadowfactory import AgentShadowFactory
from hippodamia.mymongoclient import MyMongoClient
from hippodamia.heartbeat import Heartbeat
from hippodamia.ui import UI
from hippodamia.schema.monitoringservice import get_schema
from hippodamia.hierarchicalview import HierarchicalView
from hippodamia.enums import Enforcement
from hippodamia.onboarding import Onboarding


class Monitoringservice(AbstractMicroservice):
    _version = hippodamia.version

    _protocol_version = 1

    _agentshadows = None
    _asfactory = None
    _update_available = None
    _mongo_client = None
    _heartbeat = None
    _ui = None
    _hierarchical_view = None
    _onboarding = None

    _enforcement = None

    _topic_onboarding_request = None
    _topic_cmd_ping = None
    _topic_cmd_runtime = None
    _topic_cmd_config = None
    _topic_cmd_reonboarding = None
    _topic_cmd_end = None

    def __init__(self, config, mqtt_client=None, logger=None):
        """
        Constructor - creates the services and the tasks

        :param config: config yaml structure
        :param mqtt_client: mqtt client instance
        :param logger: logger instance
        """
        AbstractMicroservice.__init__(self, config, "monitoringservice", mqtt_client, logger, logger_name=__class__.__name__)
        self._mongo_client = MyMongoClient(self._config["mongodb"], self._logger)
        self._heartbeat = Heartbeat(self._config["topics"]["heartbeat"], self._config["timings"]["heartbeat_interval"],
                                    self._mqtt_client, self._logger)

        self._topic_onboarding_request = self._config["topics"]["onboarding-request"]
        self._topic_cmd_ping = self._config["topics"]["command-ping-on-request"]
        self._topic_cmd_runtime = self._config["topics"]["command-runtime-on-request"]
        self._topic_cmd_config = self._config["topics"]["command-config-on-request"]
        self._topic_cmd_reonboarding = self._config["topics"]["command-reonboarding"]
        self._topic_cmd_end = self._config["topics"]["command-end"]

        self._update_available = threading.Event()
        self._update_available.clear()

        self._asfactory = AgentShadowFactory(self._config["topics"], self._config["timings"], self._update_available,
                                             self._mongo_client, self._mqtt_client, self._logger)
        self._agentshadows = self._asfactory.create_agentshadows(self._config["expected-services"]["services"])

        self._enforcement = Enforcement.get_enum(self._config["expected-services"]["enforcement"])
        self._hierarchical_view = HierarchicalView(self._enforcement, self._agentshadows, self._update_available,
                                                   self._logger)

        self._onboarding = Onboarding(self._protocol_version, self._topic_onboarding_request, self._enforcement,
                                      self._agentshadows, self._asfactory, self._mqtt_client, self._logger)

        self._ui = UI(self._version, self._config, self._agentshadows, self._heartbeat, self._hierarchical_view, self._onboarding,
                      self.send_cmd_ping, self.send_cmd_runtime, self.send_cmd_config, self.send_cmd_reonboarding,
                      self.send_cmd_end, self.stop, self._logger)

    def _start(self):
        self._mongo_client.start()
        self._heartbeat.start()
        for k, v in self._agentshadows.items():
            v.start()
        self._hierarchical_view.start()
        self._onboarding.start()
        self.send_cmd_reonboarding(gid=None)  # send reonboarding request to all
        self._ui.start()

    def _stop(self):
        self._ui.stop()
        self._heartbeat.stop()
        self._onboarding.stop()
        self.send_cmd_end(gid=None)  # inform everyone that the service is going down
        self._hierarchical_view.stop()
        for k, v in self._agentshadows.items():
            print("stopping {}".format(k))
            v.stop()
            import time
            time.sleep(1)
        self._mongo_client.stop()

    @classmethod
    def _get_description(cls):
        return "Hippodamia observe the state of all registered microservices (aka watch dog)."

    @classmethod
    def _get_schema(cls):
        return get_schema()

    @staticmethod
    def _render_message(request, gid):
        """
        {
            "request": "request",
            "gid": 1
        }
        """
        message = {
            "request": request
        }
        if gid is not None:
            message["gid"] = gid
        return json.dumps(message)

    def send_cmd_ping(self, gid=None):
        if gid is None:
            self._logger.info("send_cmd_ping: send request to all monitored services")
        else:
            self._logger.info("send_cmd_ping: send request to gid: {}".format(gid))
        message = self._render_message("ping", gid)
        self._mqtt_client.publish(self._topic_cmd_ping, message)

    def send_cmd_runtime(self, gid=None):
        if gid is None:
            self._logger.info("send_cmd_runtime: send request to all monitored services")
        else:
            self._logger.info("send_cmd_runtime: send request to gid: {}".format(gid))
        message = self._render_message("runtime", gid)
        self._mqtt_client.publish(self._topic_cmd_runtime, message)

    def send_cmd_config(self, gid=None):
        if gid is None:
            self._logger.info("send_cmd_config: send request to all monitored services")
        else:
            self._logger.info("send_cmd_config: send request to gid: {}".format(gid))
        message = self._render_message("config", gid)
        self._mqtt_client.publish(self._topic_cmd_config, message)

    def send_cmd_reonboarding(self, gid=None):
        if gid is None:
            self._logger.info("send_cmd_reonboarding: send request to all monitored services")
        else:
            self._logger.info("send_cmd_reonboarding: send request to gid: {}".format(gid))
        message = self._render_message("reonboarding", gid)
        self._mqtt_client.publish(self._topic_cmd_reonboarding, message)

    def send_cmd_end(self, gid=None):
        if gid is None:
            self._logger.info("send_cmd_end: send request to all monitored services")
        else:
            self._logger.info("send_cmd_end: send request to gid: {}".format(gid))
        message = self._render_message("end", gid)
        self._mqtt_client.publish(self._topic_cmd_end, message)


def standalone():
    Monitoringservice.standalone()


if __name__ == "__main__":
    Monitoringservice.standalone()

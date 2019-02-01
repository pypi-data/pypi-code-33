import datetime
import hashlib
import json
import os
import socket
import time
import uuid
from threading import Event

import pelops.myconfigtools
import psutil

import hippodamia_agent.states.create_state_machine
from hippodamia_agent.get_schema import get_schema
from hippodamia_agent.states.event_ids import event_ids
from hippodamia_agent.states.state_ids import state_ids


class MonitoringAgent:
    _config = None
    _mqtt_client = None
    _service = None
    _logger = None
    _protcol_version = 1

    _uuid = None

    _onboarding_topic_prefix = None
    _topic_send_onboarding_request = None
    _location = None
    _room = None
    _device = None
    _description = None
    _name = None
    _gid = None
    _timings = None

    _TIME_FORMAT = "%Y-%m-%dT%H:%M:%S.%fZ"  # time format string for influxdb queries

    _topic_send_ping = None
    _topic_send_runtime = None
    _topic_send_config = None
    _topic_send_end = None
    _topic_send_logger = None

    _topic_recv_cmd_sigint = None
    _topic_recv_cmd_reonboarding = None
    _topic_recv_cmd_ping_on_request = None
    _topic_recv_cmd_config_on_request = None
    _topic_recv_cmd_runtime_on_request = None
    _topic_recv_heartbeat = None

    _topic_recv_onboarding_response = None

    _state_machine = None
    _sigint = None

    def __init__(self, config, service, mqtt_client, logger):
        self._config = config
        self._mqtt_client = mqtt_client
        self._logger = logger
        self._service = service

        self._onboarding_topic_prefix = self._config["response-prefix"]
        self._topic_send_onboarding_request = self._config["onboarding-topic"]
        self._location = self._config["location"]
        self._room = self._config["room"]
        self._device = self._config["device"]
        self._gid = self._config["gid"]
        self._name = self._config["name"]
        self._description = self._config["description"]
        self._timings = self._config["timings"]

        self._start_time = time.time()
        self._init_state_machine()

    @staticmethod
    def get_schema():
        return get_schema()

    def _init_state_machine(self):
        self._sigint = Event()
        self._state_machine, states = hippodamia_agent.states.create_state_machine\
            .create(self._sigint, self._timings["restart-onboarding"],
                    self._timings["expect-heartbeat"], self._logger)

        states[state_ids.Uninitialized].update_uuid = self.update_uuid
        states[state_ids.Uninitialized].decativate_last_will = self.deactivate_last_will

        states[state_ids.Initialized].activate_onboarding_response = self.activate_onboarding_response
        states[state_ids.Initialized].send_onboarding_request = self.send_onboarding_request

        # states[state_ids.Onboarding] - nothing to config

        states[state_ids.Onboarded].send_config = self.send_config
        states[state_ids.Onboarded].deactivate_onboarding_response = self.deactivate_onboarding_response
        states[state_ids.Onboarded].activate_last_will = self.activate_last_will

        states[state_ids.Active].send_config = self.send_config
        states[state_ids.Active].send_config_interval = self._timings["send-config"]
        states[state_ids.Active].send_ping = self.send_ping
        states[state_ids.Active].send_ping_interval = self._timings["send-ping"]
        states[state_ids.Active].send_runtime = self.send_runtime
        states[state_ids.Active].send_runtime_interval = self._timings["send-runtime"]
        states[state_ids.Active].activate_config_on_request = self.activate_config_on_request
        states[state_ids.Active].deactivate_config_on_request = self.deactivate_config_on_request
        states[state_ids.Active].activate_ping_on_request = self.activate_ping_on_request
        states[state_ids.Active].deactivate_ping_on_request = self.deactivate_ping_on_request
        states[state_ids.Active].activate_runtime_on_request = self.activate_runtime_on_request
        states[state_ids.Active].deactivate_runtime_on_request = self.deactivate_runtime_on_request
        states[state_ids.Active].activate_reonboarding_request = self.activate_reonboarding_request
        states[state_ids.Active].deactivate_reonboarding_request = self.deactivate_reonboarding_request
        states[state_ids.Active].activate_forward_logger = self.activate_forward_logger
        states[state_ids.Active].deactivate_forward_logger = self.deactivate_forward_logger

        states[state_ids.Terminating].send_offboarding_message = self.send_end_message

    def start(self):
        self._state_machine.firststart()

    def stop(self):
        self._sigint.set()
        self._state_machine.operate(event_ids.sigint)

    def activate_forward_logger(self):
        self._logger.error("activate_forward_logger - NoImplementedError")

    def deactivate_forward_logger(self):
        self._logger.error("deactivate_forward_logger - NoImplementedError")

    def activate_receive_heartbeat(self):
        self._logger.debug("activate_receive_heartbeat")
        self._mqtt_client.subscribe(self._topic_recv_heartbeat, self.handler_receive_heartbeat)

    def deactivate_receive_heartbeat(self):
        self._logger.debug("deactivate_receive_heartbeat")
        self._mqtt_client.unsubscribe(self._topic_recv_heartbeat, self.handler_receive_heartbeat)

    def handler_receive_heartbeat(self, message):
        """
        {
            "heartbeat": "heartbeat",
            "timestamp": "1985-04-12T23:20:50.520Z"
        }
        """
        if message["heartbeat"] != "heartbeat":
            self._logger.error("received heartbeat message with wrong content: '{}'".format(message))
        self._logger.info("received heartbeat message")
        self._state_machine.restarttimeoutevent()

    def activate_reonboarding_request(self):
        self._logger.debug("activate_reonboarding_request")
        self._mqtt_client.subscribe(self._topic_recv_onboarding_response, self.handler_reonboarding_request)

    def deactivate_reonboarding_request(self):
        self._logger.debug("deactivate_reonboarding_request")
        self._mqtt_client.unsubscribe(self._topic_recv_onboarding_response, self.handler_reonboarding_request)

    def handler_reonboarding_request(self, message):
        """
        {
            "request": "request",
            "gid": 1
        }
        """
        if message["request"] != "request":
            self._logger.error("monitoringagent.handler_reonboarding_request - field request should contain 'request' "
                               "but contained '{}' instead", format(message["request"]))
        elif "gid" in message and message["gid"] != self._gid:
            self._logger.debug("received reonboarding request with different gid (incoming '{}', self '{})".
                               format(message["gid"], self._gid))
        else:
            self._logger.warning("received reonboarding request")
            self._state_machine.operate(event_ids.reonboarding_request)

    def activate_onboarding_response(self):
        self._logger.debug("activate_onboarding_response")
        self._mqtt_client.subscribe(self._topic_recv_onboarding_response, self.handler_onboarding_response)

    def deactivate_onboarding_response(self):
        self._logger.debug("deactivate_onboarding_response")
        self._mqtt_client.unsubscribe(self._topic_recv_onboarding_response, self.handler_onboarding_response)

    def handler_onboarding_response(self, message):
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
        if message["uuid"] != self._uuid:
            self._logger.error("received onboarding response with wrong uuid - expected '{}', received '{}"
                               .format(self._uuid, message["uuid"]))
        else:
            self._logger.warning("received onboarding response with gid '{}'".format(message["gid"]))
            self._logger.debug("onboarding response: {}".format(message))

            self._gid = message["gid"]

            self._topic_send_ping = message["topics-activity"]["ping"]
            self._logger.info("_topic_send_ping='{}'".format(self._topic_send_ping))
            self._topic_send_runtime = message["topics-activity"]["runtime"]
            self._logger.info("_topic_send_runtime='{}'".format(self._topic_send_runtime))
            self._topic_send_config = message["topics-activity"]["config"]
            self._logger.info("_topic_send_config='{}'".format(self._topic_send_config))
            self._topic_send_end = message["topics-activity"]["end"]
            self._logger.info("_topic_send_end='{}'".format(self._topic_send_end))
            self._topic_send_logger = message["topics-activity"]["logger"]
            self._logger.info("_topic_send_logger='{}'".format(self._topic_send_logger))

            self._topic_recv_cmd_sigint = message["topics-commands"]["sigint"]
            self._logger.info("_topic_recv_cmd_sigint='{}'".format(self._topic_recv_cmd_sigint))
            self._topic_recv_cmd_reonboarding = message["topics-commands"]["reonboarding"]
            self._logger.info("_topic_recv_cmd_reonboarding='{}'".format(self._topic_recv_cmd_reonboarding))
            self._topic_recv_cmd_ping_on_request = message["topics-commands"]["ping_on_request"]
            self._logger.info("_topic_recv_cmd_ping_on_request='{}'".format(self._topic_recv_cmd_ping_on_request))
            self._topic_recv_cmd_config_on_request = message["topics-commands"]["config_on_request"]
            self._logger.info("_topic_recv_cmd_config_on_request='{}'".format(self._topic_recv_cmd_config_on_request))
            self._topic_recv_cmd_runtime_on_request = message["topics-commands"]["runtime_on_request"]
            self._logger.info("_topic_recv_cmd_runtime_on_request='{}'".format(self._topic_recv_cmd_runtime_on_request))

    def activate_ping_on_request(self):
        self._mqtt_client.subscribe(self._topic_recv_cmd_ping_on_request, self.handler_ping_on_request)

    def deactivate_ping_on_request(self):
        self._mqtt_client.unsubscribe(self._topic_recv_cmd_ping_on_request, self.handler_ping_on_request)

    def handler_ping_on_request(self, message):
        """
        {
            "request": "request",
            "gid": 1
        }
        """
        if message["request"] != "request":
            self._logger.error("handler_ping_on_request - field request should contain 'request' "
                               "but contained '{}' instead", format(message["request"]))
        elif "gid" in message and message["gid"] != self._gid:
            self._logger.debug("received ping_on_request with different gid (incoming '{}', self '{})".
                               format(message["gid"], self._gid))
        else:
            self._logger.info("handler_ping_on_request")
            self.send_ping()

    def activate_runtime_on_request(self):
        self._mqtt_client.subscribe(self._topic_recv_cmd_runtime_on_request, self.handler_runtime_on_request)

    def deactivate_runtime_on_request(self):
        self._mqtt_client.unsubscribe(self._topic_recv_cmd_runtime_on_request, self.handler_runtime_on_request)

    def handler_runtime_on_request(self, message):
        """
        {
            "request": "request",
            "gid": 1
        }
        """
        if message["request"] != "request":
            self._logger.error("handler_runtime_on_request - field request should contain 'request' "
                               "but contained '{}' instead", format(message["request"]))
        elif "gid" in message and message["gid"] != self._gid:
            self._logger.debug("received runtime_on_request with different gid (incoming '{}', self '{})".
                               format(message["gid"], self._gid))
        else:
            self._logger.info("handler_runtime_on_request")
            self.send_runtime()

    def activate_config_on_request(self):
        self._mqtt_client.subscribe(self._topic_recv_cmd_config_on_request, self.handler_config_on_request)

    def deactivate_config_on_request(self):
        self._mqtt_client.unsubscribe(self._topic_recv_cmd_config_on_request, self.handler_config_on_request)

    def handler_config_on_request(self, message):
        """
        {
            "request": "request",
            "gid": 1
        }
        """
        if message["request"] != "request":
            self._logger.error("handler_config_on_request - field request should contain 'request' "
                               "but contained '{}' instead", format(message["request"]))
        elif "gid" in message and message["gid"] != self._gid:
            self._logger.debug("received config_on_request with different gid (incoming '{}', self '{})".
                               format(message["gid"], self._gid))
        else:
            self._logger.info("handler_config_on_request")
            self.send_config()

    def send_onboarding_request(self):
        self._logger.warning("send onboarding request with uuid '{}'".format(self._uuid))
        message = str(self._generate_on_boarding_request_message(self._uuid))
        self._logger.debug("onboarding request message: ".format(message))
        self._mqtt_client.publish(self._topic_send_onboarding_request, message)

    def send_ping(self):
        self._logger.info("send ping")
        message = str(self._generate_ping_message())
        self._logger.debug("ping message: {}".format(message))
        self._mqtt_client.publish(self._topic_send_ping, message)

    def send_runtime(self):
        self._logger.info("send runtime")
        message = str(self._generate_runtime_message())
        self._logger.debug("runtime message: {}".format(message))
        self._mqtt_client.publish(self._topic_send_runtime, message)

    def send_config(self):
        self._logger.info("send config")
        message = str(self._generate_config_message())
        self._logger.debug("config message: {}".format(message))
        self._mqtt_client.publish(self._topic_send_config, message)

    def send_end_message(self):
        self._logger.warning("send end message")
        message = str(self._generate_end_message())
        self._logger.debug("end message: {}".format(message))
        if self._topic_send_end is None:
            self._logger.info("send_end_message - _topic_send_end not set. skipping send.")
        else:
            self._mqtt_client.publish(self._topic_send_end, message)

    def activate_last_will(self):
        if self._topic_send_end is None:
            self._logger.info("activate_last_will - last will not set, topic is None")
        else:
            self._mqtt_client.set_will(self._topic_send_end, self._generate_end_message(last_will=True))

    def deactivate_last_will(self):
        if self._topic_send_end is None:
            self._logger.info("deactivate_last_will - last will not reset, topic is None")
        else:
            self._mqtt_client.set_will(self._topic_send_end, "")

    def update_uuid(self):
        self._uuid = uuid.uuid4()
        self._topic_recv_onboarding_response = self._onboarding_topic_prefix + str(self._uuid)
        self._logger.debug("update_uuid - new uuid: '{}'.".format(self._uuid))
        self._logger.info("update_uuid - resulting onboarding response topic: '{}'"
                          .format(self._topic_recv_onboarding_response))

    @staticmethod
    def _get_local_ip(remote_ip, remote_port):
        connections = psutil.net_connections()
        laddrs = set()
        for pconn in connections:
            try:
                if pconn.raddr[0] == remote_ip and pconn.raddr[1] == remote_port:
                    ip = pconn.laddr[0]
                    laddrs.add(ip)
            except IndexError:
                pass
        if len(laddrs) == 0:
            raise KeyError("No outgoing connection for {}:{} found.".format(remote_ip, remote_port))
        elif len(laddrs) > 1:
            raise KeyError("More than one outgoing connection ({}) found for {}:{}.".
                           format(laddrs, remote_ip, remote_port))
        return list(laddrs)[0]

    @staticmethod
    def _get_local_ips(skip_lo=True):
        laddrs = set()
        nics = psutil.net_if_addrs()
        if skip_lo:
            nics.pop("lo")
        for nic_id, nic_entries in nics.items():
            for snicaddr in nic_entries:
                if snicaddr.family == socket.AF_INET or snicaddr.family == socket.AF_INET6:
                    laddrs.add(snicaddr.address)
        return sorted(list(laddrs))

    @staticmethod
    def _get_mac_addresses(skip_lo=True):
        mac_adresses = []
        nics = psutil.net_if_addrs()
        if skip_lo:
            nics.pop("lo")
        for nic_id, nic_entries in nics.items():
            for snicaddr in nic_entries:
                if snicaddr.family == psutil.AF_LINK:
                    mac_adresses.append(snicaddr.address)
        return mac_adresses

    @staticmethod
    def _get_mac_address(interface):
        mac_adresses = []
        nics = psutil.net_if_addrs()
        for snicaddr in nics[interface]:
            if snicaddr.family == psutil.AF_LINK:
                mac_adresses.append(snicaddr.address)
        if len(mac_adresses) == 0:
            raise KeyError("No mac address found for interface '{}'.".format(interface))
        elif len(mac_adresses) > 1:
            # unclear if this can actually happen. theoretically, the result from net_if_addrs would support such a case
            raise KeyError("More than one mac address ({}) found for interface '{}'.".format(mac_adresses, interface))
        return mac_adresses[0]

    @staticmethod
    def _get_interface_from_ip(ip):
        interfaces = []
        nics = psutil.net_if_addrs()
        for nic_id, nic_entry in nics.items():
            for snicaddr in nic_entry:
                if (snicaddr.family == socket.AF_INET or snicaddr.family == socket.AF_INET6) and snicaddr.address == ip:
                    interfaces.append(nic_id)
        if len(interfaces) == 0:
            raise KeyError("No interface found for ip '{}'".format(ip))
        elif len(interfaces) > 1:
            raise KeyError("More than one interface ({}) found for ip '{}'".format(interfaces, ip))
        return interfaces[0]

    def _generate_on_boarding_request_message(self, temp_uuid):
        """
        {
          "uuid": "550e8400-e29b-11d4-a716-446655440000",
          "onboarding-topic": "/hippodamia/550e8400-e29b-11d4-a716-446655440000",
          "protocol-version": 1,
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
        hashinstance = hashlib.sha256()
        hashinstance.update(json.dumps(self._service._config).encode())
        config_hash = hashinstance.hexdigest()

        target_ip = socket.gethostbyname(self._mqtt_client._config["mqtt-address"])
        target_port = self._mqtt_client._config["mqtt-port"]
        local_ip = MonitoringAgent._get_local_ip(target_ip, target_port)
        interface = MonitoringAgent._get_interface_from_ip(local_ip)
        mac_address = MonitoringAgent._get_mac_address(interface)

        message = {
            "uuid": str(temp_uuid),
            "onboarding-topic": self._onboarding_topic_prefix + str(temp_uuid),
            "protocol-version": self._protcol_version,
            "identifier": {
                "type": self._service.__class__.__name__,
                "name": self._name,
                "location": self._location,
                "room": self._room,
                "device": self._device,
                "description": self._description,
                "host-name": socket.gethostname(),
                "mqtt-client-local-ip": local_ip,
                "ips": MonitoringAgent._get_local_ips(skip_lo=False),
                "mac-addresses": MonitoringAgent._get_mac_addresses(skip_lo=True),
                "config-hash": config_hash
            }
        }

        return message

    def _generate_ping_message(self):
        """
        {
          "gid": 1,
          "timestamp": "1985-04-12T23:20:50.520Z",
          "service-uptime": 12345.67
        }
        :return:
        """
        return {
            "gid": self._gid,
            "timestamp": datetime.datetime.now().strftime(self._TIME_FORMAT),
            "service-uptime": time.time() - self._start_time
        }

    def _generate_runtime_message(self):
        """
        {
          "gid": 1,
          "timestamp": "1985-04-12T23:20:50.520Z",
          "service-uptime": 12345.67,
          "system-uptime": 12345.67,
          "cpu_percent": 0,
          "free-memory": 0,
          "service-memory": 0,
          "disk-usage": 0,
          "messages-received-total": 0,
          "messages-sent-total": 0,
          "topics": [
            {
              "messages-received": 0,
              "messages-sent": 0,
              "topic": "/hippodamia/commands"
            }
          ]
          "service": {}
        }
        :return:
        """

        process = psutil.Process(os.getpid())

        if len(process.children()) > 0:
            self._logger.warning("process has children (not threads) -> cpu_percent_process and mem_percent_process "
                                 "do not include the values from the children.")

        process_memory_info = process.memory_info()
        total_memory_info = psutil.virtual_memory()
        recv, sent = self._mqtt_client._stats.get_totals()

        message = {
            "gid": self._gid,
            "timestamp": datetime.datetime.now().strftime(self._TIME_FORMAT),
            "service-uptime": time.time() - self._start_time,
            "system-uptime": time.time() - psutil.boot_time(),
            "cpu_percent_total": round(psutil.cpu_percent(), 1),
            "cpu_percent_process": round(process.cpu_percent() / psutil.cpu_count(), 1),
            "mem_percent_total": round(total_memory_info.percent, 1),
            "mem_percent_process": round(process.memory_percent(), 2),
            "service-memory": round((process_memory_info.rss + process_memory_info.vms) / (1024*1024), 2),
            "disk-free": round(psutil.disk_usage("/").free / (1024*1024), 2),
            "messages-received-total": recv,
            "messages-sent-total": sent,
            "topics": [],
            "service": self._service.runtimeinformation()
        }

        for topic, stats in self._mqtt_client._stats.stats.items():
            entry = {
                "messages-received": stats.messages_received,
                "messages-sent": stats.messages_sent,
                "topic": topic
            }
            message["topics"].append(entry)

        return message

    @staticmethod
    def mask_entries(config, patterns, mask_string="*****"):
        if type(config) is dict:
            for k, c in config.items():
                if type(c) is list or type(c) is dict:
                    MonitoringAgent.mask_entries(c, patterns, mask_string)
                elif type(c) is str:
                    for pattern in patterns:
                        if pattern in k:
                            config[k] = mask_string
                            break
        elif type(config) is list:
            for c in config:
                MonitoringAgent.mask_entries(c, patterns, mask_string)

    def _generate_config_message(self):
        """
        {
          "gid": 1,
          "timestamp": "1985-04-12T23:20:50.520Z",
          "service-uptime": 12345.67,
          "config": {}
        }
        :return:
        """
        config_clone = pelops.myconfigtools.dict_deepcopy_lowercase(self._config)
        MonitoringAgent.mask_entries(config_clone, ["credentials", "password", "user"])

        return {
            "gid": self._gid,
            "timestamp": datetime.datetime.now().strftime(self._TIME_FORMAT),
            "service-uptime": time.time() - self._start_time,
            "config": config_clone
        }

    def _generate_end_message(self, last_will=False):
        """
        {
          "gid": 1
          "reason": last_will  # ["last_will", "agent"]
        }
        :return:
        """
        message = {
            "gid": self._gid,
            "reason": "agent"
        }

        if last_will:
            message["reason"] = "last_will"

        return message

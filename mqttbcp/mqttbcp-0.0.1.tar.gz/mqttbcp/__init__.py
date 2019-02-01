import json
import time

import paho.mqtt.client as mqtt
import uuid
from typing import Dict, List


class Client:

    commands = {}

    def on_command(self, client, userdata, msg):
        try:
            data = json.loads(msg.payload)
        except ValueError:
            data = None
        if not data:
            return
        cmd = data.get("cmd")
        com = self.commands.get(cmd)
        if not com:
            return
        ret = com(self, userdata, msg.topic, data)
        if not ret:
            return
        return {"id": self.client_id, "cmd": cmd + "R", "time": time.time(), "ret": ret}

    def on_message(self, client, userdata, msg):
        print("Message: " + msg.topic + " " + str(msg.payload))
        answer = self.on_command(client, userdata, msg)
        if answer:
            client.publish(msg.topic, json.dumps(answer))

    def on_connect(self, client, userdata, flags, rc):
        print("Connected with result code " + str(rc))
        print("Connected as " + self.client_id)

        for topic, qos in self.rooms.items():
            client.subscribe(topic, qos)

    def on_log(self, client, userdata, level, buf):
        print("log: ", buf)

    def __init__(
            self,
            name: str,
            desc: str,
            client_id: str = "",
            rooms: Dict[str, int] = None,
            tags: List[str] = None
    ):

        self.name = name
        self.desc = desc
        self.client_id = client_id if client_id else str(uuid.uuid4())
        self.rooms = rooms if rooms else {}
        self.tags = tags if tags else []
        self.client = None

    def create(
            self,
            clean_session: bool = False,
            protocol: int = mqtt.MQTTv311,
            transport: str = "tcp",
            debug: bool = False
    ):

        self.client = mqtt.Client(self.client_id, clean_session, None, protocol, transport)

        self.client.on_connect = self.on_connect
        self.client.on_log = self.on_log if debug else None
        self.client.on_message = self.on_message

    def connect(
            self,
            host: str,
            port: int = 1883,
            keepalive: int = 60,
            bind_address: str = ""
    ):

        self.client.connect(host, port, keepalive, bind_address)
        self.client.loop_start()


from mqttbcp import commands

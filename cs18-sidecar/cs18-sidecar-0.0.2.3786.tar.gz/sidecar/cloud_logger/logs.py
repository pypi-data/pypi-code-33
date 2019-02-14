from typing import List, Tuple
from datetime import datetime
from abc import ABC, abstractmethod


class LogEntry(object):
    def __init__(self, app: str, instance: str, topic: str, log_events: List[Tuple[datetime, str]], log_type: str):
        self.app = app
        self.instance = instance
        self.topic = topic
        self.log_events = log_events
        self.log_type = log_type

    def get_as_string(self) -> str:
        log_events_str = "\n".join(str(time) + " " + message for time, message in self.log_events)
        return "app: " + self.app + "\ninstance: " + self.instance + "\ntopic: " + self.topic + "\n" + log_events_str


class ICloudLogger(ABC):
    @classmethod
    @abstractmethod
    def write(cls, log_entry: LogEntry):
        pass

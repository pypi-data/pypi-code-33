import json
from abc import ABC, abstractmethod


class BaseQueueAdapter(ABC):

    @abstractmethod
    def publish(self, channel, data):
        pass

    @abstractmethod
    def consume(self, channel, timeout=None):
        pass


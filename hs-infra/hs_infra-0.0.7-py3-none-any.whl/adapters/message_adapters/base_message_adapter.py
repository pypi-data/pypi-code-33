from abc import abstractmethod
from time import sleep

from hs_infra.managers.message.message_redis_manager import MessageRedisManager
from hs_infra.meta_classes.singleton_meta_class import Singleton


class BaseMessageAdapter(metaclass=Singleton):
    """Do not use this Adapter Directly as your adapter."""

    def __init__(self):
        self.redis_manager = MessageRedisManager()

    @abstractmethod
    def add_to_contact_list(self, receptor: str):
        raise NotImplementedError()

    @abstractmethod
    def push_to_queue(self, message: str, receptor: str):
        raise NotImplementedError()

    @abstractmethod
    def _send_message(self, value):
        raise NotImplementedError()

    def send_queued_message(self):
        while True:
            value = self.redis_manager.read_from_queue()
            if value is None:
                break
            ok, _ = self._send_message(value)
            if not ok:
                self.redis_manager.push_to_queue(value)
                sleep(5)

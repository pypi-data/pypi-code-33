from hs_infra.managers.base.base_redis_manager import BaseRedisManager
from hs_infra.meta_classes.singleton_meta_class import Singleton


class MessageRedisManager(BaseRedisManager, metaclass=Singleton):
    MESSAGE_KEY = 'message_queue'

    def __init__(self, **params):
        super().__init__(**params)

    def push_to_queue(self, value: str):
        return self.get_connection().rpush(self.MESSAGE_KEY, value)

    def read_from_queue(self):
        return self.get_connection().lpop(self.MESSAGE_KEY)

import json
import uuid

import redis

from multiqq.adapters import BaseQueueAdapter

CLIENT_ID = str(uuid.uuid4())


class RedisQueueAdapter(BaseQueueAdapter):

    def __init__(self, group_name, host, port=6379, pooling_timeout=30000):
        self.group_name = group_name
        self.pooling_timeout = pooling_timeout

        self.host = host
        self.port = port
        self.queue = redis.Redis(host=host, port=port)

    def publish(self, channel, data):
        return self.queue.xadd(channel, {'body': json.dumps(data)}).decode('ascii')

    # @retry(
    #     reraise=True,
    #     retry=retry_if_exception_type(redis.exceptions.ConnectionError),
    #     wait=wait_random_exponential(multiplier=1, max=600),
    #     stop=stop_after_delay(30)
    # )
    def consume(self, channel, timeout=None):
        while True:
            groups = self.queue.xreadgroup(self.group_name, CLIENT_ID, {channel: '>'}, block=self.pooling_timeout)
            for stream, messages in groups:
                for message_id, message in messages:
                    yield (message_id.decode('ascii'), message)

    def xpto(self):
        self.queue.xgroup_create('newstream', 'newstream-client', 0, True)


if __name__ == '__main__':
    r = RedisQueueAdapter('newstream-client', 'localhost')
    r.xpto()
    print(r.publish('newstream', {'a': 'b', 'c': 3}))
    for id, data in r.consume('newstream'):
        print(id)
        print(data)

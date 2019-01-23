import json

import greenstalk
from tenacity import retry, stop_after_delay, wait_fixed, wait_random

from multiqq.adapters import BaseQueueAdapter


class BeanstalkdQueueAdapter(BaseQueueAdapter):

    def __init__(self, host, port=11300, serializer=None):
        self.host = host
        self.port = port
        self.connection = greenstalk.Client(host=host, port=port)

    @retry(reraise=True, stop=stop_after_delay(30), wait=wait_fixed(3) + wait_random(0, 2))
    def publish(self, pipe, data):
        return self.connection.put(json.dumps(data))

        # raise Exception('fuuuuu')

    def consume(self, channel, timeout=None):
        while True:
            x = self.connection.reserve(timeout=timeout)
            print(x)
            print(x.id)
            yield x.body


# if __name__ == '__main__':
#     x = BeanstalkdQueueAdapter('127.0.0.1')
#     # x.publish('nada', 'nada %s' % time.time())
#     for bla in x.consume(''):
#         print(bla)
#
if __name__ == '__main__':
    r = BeanstalkdQueueAdapter('localhost')
    print(r.publish('test', {'a': 'b'}))

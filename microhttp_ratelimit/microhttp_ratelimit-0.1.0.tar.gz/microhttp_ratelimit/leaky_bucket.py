from time import time
from redis import StrictRedis


class RedisLeakyBucketRateLimit:

    def __init__(self, redis_connection: StrictRedis, namespace, period, limit):
        self.redis_connection = redis_connection
        self.pipe_line_connection = self.redis_connection.pipeline(True)
        self.namespace = namespace
        self.period = period
        self.limit = limit

    def _can_attempt(self, add_attempt=True) -> bool:
        """
        Checks if a namespace is rate limited or not with
        including/excluding the current call.

        :param add_attempt: Boolean value indicating if the current call
                            should be considered as an attempt or not
        :type add_attempt: bool
        :return: Returns true if attempt can go ahead under current rate
                 limiting rules, false otherwise
        """
        connection = self.pipe_line_connection
        current_time = int(round(time() * 1000000))
        old_time_limit = current_time - (self.period * 1000000)
        connection.zremrangebyscore(self.namespace, 0, old_time_limit)
        connection.expire(self.namespace, self.period)
        current_count = 1
        if add_attempt:
            connection.zadd(self.namespace, {current_time: current_time})
        connection.zcard(self.namespace)
        redis_result = connection.execute()
        current_count += redis_result[-1]
        return current_count <= self.limit

    def attempt(self):
        """
        Records an attempt and returns true of false depending on whether
        attempt can go through or not.

        :return: Returns true if attempt can go ahead under current rate
                 limiting rules, false otherwise
        """
        return self._can_attempt()

    def is_rate_limited(self) -> bool:
        """
        Checks if a namespace is already rate limited or not without making
        any additional attempts.

        :return: Returns true if attempt can go ahead under current rate
                 limiting rules, false otherwise
        """
        return not self._can_attempt(add_attempt=False)

    def get_attempt_expiration_time(self):
        return int(self.redis_connection.ttl(self.namespace))

    def reset(self):
        """ Reset limits """
        self.redis_connection.delete(self.namespace)

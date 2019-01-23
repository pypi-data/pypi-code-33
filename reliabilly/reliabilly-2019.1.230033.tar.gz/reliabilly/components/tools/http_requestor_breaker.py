from circuitbreaker import CircuitBreaker
from requests import RequestException


# pylint: disable=too-few-public-methods
class HttpRequestorBreaker:
    def __init__(self, name, failure_threshold=5, recovery_timeout=60, expected_exception=RequestException):
        self.breaker = CircuitBreaker(failure_threshold, recovery_timeout, expected_exception, name)

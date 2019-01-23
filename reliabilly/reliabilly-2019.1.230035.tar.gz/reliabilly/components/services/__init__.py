from enum import Enum
from reliabilly.settings import Constants


class ResultTypes(Enum):
    UNKNOWN = 'unknown'
    SUCCESS = 'success'
    ERROR = 'error'
    NO_RESULT = 'no_result'
    THRESHOLD = 'threshold'


class QueryResult:  # pylint: disable=too-few-public-methods
    value: float
    result: ResultTypes
    message: str

    def __init__(self, value=None, result=ResultTypes.UNKNOWN, message=Constants.EMPTY):
        self.value = value
        self.result = result
        self.message = message

    def __str__(self):
        return f'Result Value: {self.value}, Result: {self.result}, Message: {self.message}'

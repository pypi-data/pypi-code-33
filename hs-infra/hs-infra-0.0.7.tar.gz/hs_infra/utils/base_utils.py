import uuid
from collections import Iterable


class BaseUtils:

    @classmethod
    def generate_uuid_token(cls, length: int = None, numeric: bool = False) -> str:
        """Use uuid package to generate random tokens.
        :parameter length: arbitrary length for token.
        :parameter numeric: force to generate decimal digits string.
        :return hexadecimal string if numeric is false else decimal one.
        """
        if numeric:
            random_uuid = str(uuid.uuid4().int)
        else:
            random_uuid = uuid.uuid4().hex

        if length is None:
            return random_uuid
        else:
            return random_uuid[:length]

    @classmethod
    def is_iterable(cls, obj, exclude_str=True) -> bool:
        is_iterable = False
        if isinstance(obj, Iterable):
            if isinstance(obj, str) and exclude_str is False:
                is_iterable = True
        return is_iterable

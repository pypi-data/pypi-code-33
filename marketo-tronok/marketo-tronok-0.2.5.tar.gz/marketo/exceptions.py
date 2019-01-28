
class MktoSoapException(Exception):
    def __init__(self, error_code, *args: object, **kwargs: object) -> None:
        super().__init__(*args, **kwargs)
        self.error_code = error_code


class MktoRateLimitExceedException(MktoSoapException):
    pass
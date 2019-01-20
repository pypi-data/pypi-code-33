class CallableOrListOfCallables:

    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, v):
        if isinstance(v, list):
            for supposedly_callable in v:
                if not callable(supposedly_callable):
                    raise TypeError(f'Object must be callable, cannot be {v}.')
            return v
        elif not callable(v):
            raise TypeError(f'Object must be callable, cannot be {v}.')
        return [v]


class PipelineCache:

    required_methods = ['get', 'set']

    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, v):
        for method in cls.required_methods:
            if not hasattr(v, method):
                raise NotImplementedError(f'Your cache class must implement a {method} method.')
            elif not callable(getattr(v, method)):
                raise NotImplementedError(f'The {method} implemented by your cache class is not callable.')
        return v


class ErrorHandler:

    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, v):
        if not isinstance(v, list):
            v = [v]
        for _handler in v:
            if isinstance(_handler, dict):
                exception_class = _handler.get('exception_class', False)
                handler = _handler.get('handler', False)
                if not exception_class or not handler:
                    raise NotImplementedError('Your error handlers must indicate both an exception '
                                              'class and a handler function.')
            elif not hasattr(_handler, 'exception_class') or not hasattr(_handler, 'handler'):
                raise NotImplementedError('Your error handlers must indicate both an exception '
                                          'class and a handler function.')
            else:
                exception_class = _handler.exception_class
                handler = _handler.handler

            if not issubclass(exception_class, BaseException):
                raise ValueError(f'Your error handlers must handle exceptions that inherit from BaseException')
            elif not callable(handler):
                raise ValueError('Your error handlers must be callable.')
        return v
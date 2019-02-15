from pydantic import ValidationError


class ExceptionHandler:
    """
    pydantic doesn't support List and Tuple yet, unfortunately, so this cannot inherit from BaseModel

    exception_class: Optional[ExceptionType]
    exception_classes: Optional[List[ExceptionType]]
    handler: Callable[..., Type]
    """
    # keeping old exception_class syntax for backwards compatibility
    def __init__(self, exception_class=None, handler=None, exception_classes=None):
        if exception_classes is not None and exception_class is not None:
            raise ValueError('ExceptionHandler requires one of an exception_classes or exception_class attribute.'
                             '(You gave both.)')
        elif exception_classes is None and exception_class is None:
            raise ValueError('ExceptionHandler requires either an exception_classes or exception_class attribute.')
        elif exception_classes is None:
            self.exception_classes = (exception_class, )
        else:
            self.exception_classes = tuple(exception_classes)
        self.handler = handler

    def __repr__(self):
        return f'<{self.exception_classes}: {self.handler}>'


class CallableOrListOfCallables:

    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, v):
        if isinstance(v, (list, tuple)):
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
        if v is None:
            return v
        handler_instances = []
        if not isinstance(v, (list, tuple)):
            v = [v]
        for _handler in v:
            if isinstance(_handler, dict):
                exception_classes = _handler.get('exception_classes', None)
                exception_class = _handler.get('exception_class', None)
                handler = _handler.get('handler', None)
            else:
                exception_classes = getattr(_handler, 'exception_classes', None)
                exception_class = getattr(_handler, 'exception_class', None)
                handler = getattr(_handler, 'handler', None)

            handler_instance = ExceptionHandler(exception_class, handler, exception_classes)
            for _exception_class in handler_instance.exception_classes:
                if not issubclass(_exception_class, (BaseException, Exception)):
                    raise ValidationError(f'Your error handlers must handle exceptions that inherit from BaseException '
                                          f'or Exception.')

            if not callable(handler_instance.handler):
                raise ValidationError(f'Your error handlers must be callable. Cannot be {handler_instance.handler}')

            handler_instances.append(handler_instance)
        return handler_instances

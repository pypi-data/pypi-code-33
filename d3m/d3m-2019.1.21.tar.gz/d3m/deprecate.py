import functools
import logging
import sys
import typing

logger = logging.getLogger(__name__)


class Context(typing.NamedTuple):
    function: str
    argument: str
    filename: str
    module: str
    lineno: int


def arguments(*deprecated_arguments: str) -> typing.Callable:
    """
    A decorator which issues a warning if any of the ``deprecated_arguments`` is being
    passed to the wrapped function.
    """

    def decorator(f: typing.Callable) -> typing.Callable:
        already_warned: typing.Set[Context] = set()

        @functools.wraps(f)
        def wrapper(*args: typing.Any, **kwargs: typing.Any) -> typing.Any:
            for argument in deprecated_arguments:
                if argument in kwargs:
                    frame = sys._getframe(1)
                    try:
                        if not frame:
                            logger.warning(
                                "Providing a deprecated argument '%(argument)s' to '%(function)s' function.",
                                {
                                    'argument': argument,
                                    'function': f.__name__,
                                },
                            )
                            break

                        context = Context(f.__name__, argument, frame.f_code.co_filename, frame.f_globals.get('__name__', None), frame.f_lineno)

                    finally:
                        del frame

                    if context in already_warned:
                        break
                    already_warned.add(context)

                    logger.warning("%(module)s: Providing a deprecated argument '%(argument)s' to '%(function)s' function in '%(filename)s' at line %(lineno)s.", context._asdict())

                    break

            return f(*args, **kwargs)

        return wrapper

    return decorator

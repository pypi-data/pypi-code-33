from functools import wraps
from typing import Iterable, Callable
from inspect import signature

__all__ = 'decorator', 'decoratormethod', 'before', 'after', 'decorators', 'wraps_signature'


def wraps_signature(wrapped):
    "functools.wraps but preserving the argument signature"
    def wrapper(func):
        funky = wraps(wrapped)(func)
        funky.__signature__ = signature(wrapped)
        return funky
    return wrapper


def decorator(decfunc):

    def on_decorate(*args, **kwargs):
        if args and callable(args[0]):
            # @decfunc
            return decfunc(*args, **kwargs)
        else:
            # @decfunc(x=1)
            def apply(func):
                return decfunc(func, **kwargs)
            return apply
    return on_decorate


def decoratormethod(decfunc):
    #print('method', decfunc)
    def on_decorate(self, *args, **kwargs):
        #print('methodondec', args, kwargs)
        if args and callable(args[0]):
            # @decfunc
            return decfunc(self, *args, **kwargs)
        else:
            # @decfunc(x=1)
            def apply(func):
                return decfunc(self, func, *args, **kwargs)
            return apply
    return on_decorate


@decorator
def before(func):
    "call before the decorated function runs"
    @decorator
    def decorate(func2):
        @wraps_signature(func2)
        def wrap(*args, **kwargs):
            func()
            return func2(*args, **kwargs)
        return wrap
    return decorate

@decorator
def after(func):
    "call after the decorated function runs"
    @decorator
    def decorate(func2):
        @wraps_signature(func2)
        def wrap(*args, **kwargs):
            value = func2(*args, **kwargs)
            func()
            return value
        return wrap
    return decorate


def decorators(*decorators: Iterable[Callable]):
    "bundle many decorators"
    def decorate(func):
        for dec in decorators:
            func = dec(func)
        return func
    return decorate



class decoratorlist(list):
    """
    useful as a class attribute e.g

    self.things = decoratorlist()

    @obj.things
    def my_function():
        pass

    obj.things -> [my_function]

    """

    @decoratormethod
    def __call__(self, func):
        self.append(func)

# -*- coding: utf-8 -*-

"""Implements the decorators for easy subscriptions of methods to ZEvents
"""

from functools import wraps

from .events import TickEvent


def listener(cls):
    """Class decorator to mark a class as a zevent listener."""
    func = cls.__init__

    # Wraps the class constructor to automate the subscription of methods to
    # event handlers
    @wraps(cls.__init__)
    def new_init(self, *args, **kwargs):
        func(self, *args, **kwargs)
        # Subscribe methods in __dict__ marked as handler for a given
        # event type
        for key, method in cls.__dict__.items():
            if hasattr(method, f"_zevent"):
                event = method._zevent
                event.subscribe(getattr(self, key))

    # Patching the constructor
    cls.__init__ = new_init
    return cls


def handler(event):
    """Decorator used to mark a method as handler for the given event type."""
    def decorator(func):
        setattr(func, "_zevent", event)
        return func
    return decorator

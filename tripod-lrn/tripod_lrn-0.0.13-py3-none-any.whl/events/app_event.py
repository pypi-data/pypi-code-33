# -*- coding: utf-8 -*-
"""
Module events.py
-----------------------
A class that defines a singles and generic application event.
"""
from blinker import signal


class AppEvent(object):
    """
    An application event object.
    """
    def __init__(self, name):
        self.signal = signal(name)

    def __iadd__(self, other):
        self.register_handler(other)
        return self

    def __sub__(self, other):
        self.unregister_handler(other)
        return self

    def register_handler(self, handler):
        """
        Register an function to handle the event.
        :param handler: a function pointer.
        """
        self.signal.connect(handler)

    def unregister_handler(self, handler):
        """
        Removes the handler function from the event handlers lists.
        :param handler: a function pointer.
        """
        self.signal.disconnect(handler)

    def send(self, sender=None):
        """
        An event emmiter function.
        :param sender: a reference for the emitter object.
        """
        self.signal.send(sender)

# -*- coding: utf-8 -*-

"""Module defining standard events for the ZEvents system."""

from .core import Event, TriggerEvent


class TickEvent(TriggerEvent):
    """Event raised by an application-level event loop."""

    def __init__(self, *args, **kargs):
        super().__init__(*args, **kargs)
        self.name = "Tick Event"


class QuitEvent(Event):
    """Event raised to quit an application-level event loop."""

    def __init__(self, *args, **kargs):
        super().__init__(*args, **kargs)
        self.name = "Quit Event"

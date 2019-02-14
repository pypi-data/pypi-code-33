# -*- coding: utf-8 -*-

"""Implements the ZEvents core system.
"""

from collections import defaultdict, OrderedDict
import queue
from weakref import WeakMethod


class EventManager:
    """Class responsible for the mechanics of event management.

    EventManager provides the interface to subscribe or unsubscribe a
    handler to or from the notification feed of events of different types. This
    class also provides the method to fire an event object.
    """

    def __init__(self):
        # Subscribers dictionnary. Keys are event types. Values are Orderdicts
        # of weakly-referenced functions or methods
        self._subscribers = defaultdict(OrderedDict)

        # Queues for pending subscriptions, unsubscription and notifications
        self._subscriptions = queue.Queue()
        self._unsubscriptions = queue.Queue()
        self._notifications = queue.Queue()

    def send(self, event):
        """Sends an event notification to all the subscribers."""
        self._notifications.put([type(event), event])
        # Processing of queued subscriptions, unsubscriptions and requests
        if isinstance(event, TriggerEvent):
            self._process_subscriptions()
            self._process_unsubscriptions()
            self._process_notifications()

    def subscribe(self, event_type, handler):
        """Subscribes a handler function to the notification feed of a given
        event.
        """
        self._subscriptions.put([event_type, handler])

    def unsubscribe(self, event_type, handler):
        """Unsubscribes a handler function from the notification feed of a
        given event.
        """
        self._unsubscriptions.put([event_type, handler])

    def _process_subscriptions(self):
        """Processes pending subscriptions."""
        # We empty the subscription queue
        while not self._subscriptions.empty():
            event_type, handler = self._subscriptions.get()
            weak_handler = WeakMethod(handler)
            # We subscribe the handler to all superclass events
            for klass in event_type.__mro__:
                if issubclass(klass, Event):
                    self._subscribers[klass][weak_handler] = True

    def _process_unsubscriptions(self):
        """Processes pending unsubscriptions."""
        # We empty the unsubscription queue
        while not self._unsubscriptions.empty():
            event_type, handler = self._unsubscriptions.get()
            weak_handler = WeakMethod(handler)
            # We unsubscribe the handler from all superclass events
            for klass in event_type.__mro__:
                if weak_handler in self._subscribers[klass]:
                    del self._subscribers[klass][weak_handler]

    def _process_notifications(self):
        """Processes pending notifications."""
        # We Empty the notification queue
        while not self._notifications.empty():
            event_type, event = self._notifications.get()
            for weak_handler in self._subscribers[event_type]:
                handler = weak_handler()
                handler(event)


class Event:
    """Base class of all events in the notification system.

    Event is the base class used to create all the specialized events. It
    provides default implementations to send notification for the underlying
    event or to subscribe/unsubscribe to/from the notification feed of this
    particular event.
    """

    manager = EventManager()

    def __init__(self):
        """Default constructor."""
        self.name = 'Generic Event'

    @classmethod
    def send(cls, *args, **kargs):
        """Sends a notification to all the subscribers listening to this event.
        """
        event = cls(*args, **kargs)
        cls.manager.send(event)

    @classmethod
    def subscribe(cls, handler):
        """Subscribes a handler function to the notification feed of this event.
        """
        cls.manager.subscribe(cls, handler)

    @classmethod
    def unsubscribe(cls, handler):
        """Unsubscribes a handler function from the notification feed of this
        event.
        """
        cls.manager.unsubscribe(cls, handler)

    def __str__(self):
        """Converts the current event to a string representation."""
        return f'<{type(self).__name__} at {id(self)}>'


class TriggerEvent(Event):
    """Base event triggering the processing of the queues in EventManager.

    This Event can be inherited by all events expected to trigger the
    processing of the pending subscriptions, unsubscriptions and notifications
    in the Event Manager.
    """

    def __init__(self, *args, **kargs):
        super().__init__(*args, **kargs)
        self.name = "Trigger Event"

# local
try:
    from ts3ekkosingle.event_type import EventType
except ImportError:
    from .event_type import EventType


class Command:
    """
    Lower priority of the command means lower priority in the order the commands are called.
    If a command successfully handles an event, no further command will be called for that event.
    """

    def __init__(self, event_hooks, func, priority=None, name=None, help_cmd_str=None):
        """

        :param event_hooks: single or list of EventHooks this command should trigger on
        :param func: callback for event handler
        :param priority: higher=gets called earlier, handling stops on first successful handle
        :param name:
        :param help_cmd_str: Command prefix that should be displayed in the help command list.
        """
        if name is None:
            name = func.__name__

        if type(event_hooks) == EventType:
            event_hooks = [event_hooks]
        self.event_hooks = event_hooks

        self.func = func
        self.name = name

        self.help_cmd_str = help_cmd_str

        if priority is None:
            priority = 100
        self.priority = priority

    def __repr__(self):
        return f'<EkkoCmd name: {self.name}, prio: {self.priority}, ehooks: {self.event_hooks}>'

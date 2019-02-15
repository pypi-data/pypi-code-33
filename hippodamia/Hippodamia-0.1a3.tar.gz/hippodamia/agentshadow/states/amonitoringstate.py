import datetime
from tantamount.astate import AState
import pelops.mylogger


class AMonitoringState(AState):
    logger = None
    update_available = None
    counter_on_exit = 0
    counter_on_entry = 0
    timestamp_on_entry = None
    timestamp_on_exit = None
    set_health = None
    health = None

    def __init__(self, update_available, set_health, health, logger, logger_name):
        AState.__init__(self)
        self.logger = pelops.mylogger.get_child(logger, logger_name)
        self.logger.debug("__init__ ")
        self.set_health = set_health
        self.health = health
        self.update_available = update_available

    def on_entry(self):
        self.logger.info("on_entry")
        self.counter_on_entry += 1
        self.timestamp_on_exit = None
        self.timestamp_on_entry = datetime.datetime.now()

        self.set_health(self.health)
        next = self._on_entry()

        self.update_available.set()
        if next is not None:
            self.logger.debug("on_entry - event: {}".format(next.name))
        return next

    def _on_entry(self):
        return None

    def on_exit(self):
        self.logger.info("on_exit")
        self.counter_on_exit += 1
        self.timestamp_on_exit = datetime.datetime.now()

        self._on_exit()

    def _on_exit(self):
        pass

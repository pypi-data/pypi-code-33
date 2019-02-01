from tantamount.astate import AState
from hippodamia_agent.states.event_ids import event_ids
from threading import Event
import sched
import time


class Active(AState):
    sigint = None

    send_config = None
    send_config_interval = 0
    send_ping = None
    send_ping_interval = 0
    send_runtime = None
    send_runtime_interval = 0
    activate_config_on_request = None
    deactivate_config_on_request = None
    activate_ping_on_request = None
    deactivate_ping_on_request = None
    activate_runtime_on_request = None
    deactivate_runtime_on_request = None
    activate_reonboarding_request = None
    deactivate_reonboarding_request = None
    activate_forward_errors = None
    deactivate_forward_errors = None
    activate_receive_heartbeat = None
    deactivate_receive_heartbeat = None

    _scheduler = None
    _timer = None
    _event_runtime = None
    _event_ping = None
    _event_config = None

    logger = None

    def __init__(self, logger, sigint):
        AState.__init__(self)
        self.logger = logger
        self.sigint = sigint

        self._timer = Event()
        self._scheduler = sched.scheduler(time, self._timer.wait)
        self.logger.info("State 'Active' created")

    def on_entry(self):
        self.logger.info("state on_entry: Active")

        if self.sigint.is_set():
            return event_ids.sigint

        self.activate_forward_errors()

        self.activate_runtime_on_request()
        self.activate_ping_on_request()
        self.activate_config_on_request()
        self.activate_reonboarding_request()
        self.activate_receive_heartbeat()

        self._schedule_event_config()
        self._schedule_event_ping()
        self._schedule_event_runtime()

        return None

    def _stop_scheduler(self):
        try:
            self._scheduler.cancel(self._event_config)
        except ValueError:
            pass
        try:
            self._scheduler.cancel(self._event_runtime)
        except ValueError:
            pass
        try:
            self._scheduler.cancel(self._event_ping)
        except ValueError:
            pass
        self._timer.set()
        self.logger.info("state active: stop_scheduler done")

    def on_exit(self):
        self._stop_scheduler()
        self.deactivate_runtime_on_request()
        self.deactivate_ping_on_request()
        self.deactivate_config_on_request()
        self.deactivate_reonboarding_request()
        self.deactivate_forward_errors()
        self.deactivate_receive_heartbeat()
        self.logger.info("state on_entry: Active")

    def _schedule_event_runtime(self):
        self.logger.info("state active: _schedule_event_runtime ({}s)".format(self.send_runtime_interval))
        self._event_runtime = self._scheduler.enter(self.send_runtime_interval, 0, self._execute_runtime)

    def _schedule_event_config(self):
        self.logger.info("state active: _schedule_event_config ({}s)".format(self.send_config_interval))
        self._event_config = self._scheduler.enter(self.send_config_interval, 0, self._execute_config)

    def _schedule_event_ping(self):
        self.logger.info("state active: _schedule_event_ping ({}s)".format(self.send_ping_interval))
        self._event_ping = self._scheduler.enter(self.send_ping_interval, 0, self._ping_runtime)

    def _execute_runtime(self):
        self.logger.debug("state active._execute_runtime")
        self.send_runtime()
        self._schedule_event_runtime()

    def _execute_ping(self):
        self.logger.debug("state active._execute_ping")
        self.send_ping()
        self._schedule_event_ping()

    def _execute_config(self):
        self.logger.debug("state active._execute_config")
        self.send_config()
        self._schedule_event_config()

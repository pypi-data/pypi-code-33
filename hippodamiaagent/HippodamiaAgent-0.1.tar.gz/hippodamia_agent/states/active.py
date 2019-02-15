from tantamount.astate import AState
from hippodamia_agent.states.event_ids import event_ids
import threading
from sched import scheduler
from time import time


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
    activate_end_on_request = None
    deactivate_end_on_request = None
    activate_ping_on_request = None
    deactivate_ping_on_request = None
    activate_runtime_on_request = None
    deactivate_runtime_on_request = None
    activate_reonboarding_request = None
    deactivate_reonboarding_request = None
    activate_forward_logger = None
    deactivate_forward_logger = None
    activate_receive_heartbeat = None
    deactivate_receive_heartbeat = None

    _scheduler = None
    _delay_func = None
    _schedule_thread = None
    _update_schedule_thread = None
    _stop_schedule_thread = False
    _stopping_schedule_thread = False
    _event_runtime = None
    _event_ping = None
    _event_config = None

    logger = None

    def __init__(self, logger, sigint):
        AState.__init__(self)
        self.logger = logger
        self.sigint = sigint

        self._delay_func = threading.Event()
        self._scheduler = scheduler(time, self._delay_func.wait)
        self._update_schedule_thread = threading.Event()
        self.logger.info("State 'Active' created")

    def on_entry(self):
        self.logger.info("state on_entry: Active")

        if self.sigint.is_set():
            return event_ids.SIGINT

        self.activate_forward_logger()
        self.activate_runtime_on_request()
        self.activate_ping_on_request()
        self.activate_config_on_request()
        self.activate_end_on_request()
        self.activate_reonboarding_request()
        self.activate_receive_heartbeat()

        self._start_scheduler()

        return None

    def _run_scheduler(self):
        self.logger.debug("state active: _run_scheduler started")
        self._update_schedule_thread.set()  # call scheduler.run on first call (events might have already been added)
        while not self._stop_schedule_thread:
            if self._update_schedule_thread.isSet():
                self._scheduler.run(blocking=True)
                self.logger.debug("state active: _run_scheduler expired")
            self._update_schedule_thread.wait(0.1)  # timeout for KeyboardInterrupt handling
        self.logger.debug("state active: _run_scheduler stopped")

    def _start_scheduler(self):
        self.logger.info("state active: _start_scheduler start")
        self._delay_func.clear()
        self._stopping_schedule_thread = False
        self._stop_schedule_thread = True

        self._schedule_event_config()
        self._schedule_event_runtime()
        self._schedule_event_ping()

        self._stop_schedule_thread = False
        self._update_schedule_thread.clear()

        self._schedule_thread = threading.Thread(target=self._run_scheduler)
        self._schedule_thread.start()
        self.logger.info("state active: _start_scheduler done")

    def _stop_scheduler(self):
        self.logger.info("state active: stop_scheduler start")
        self._stopping_schedule_thread = True
        self._stop_schedule_thread = True

        events = self._scheduler.queue
        for event in events:
            self._scheduler.cancel(event)

        self._delay_func.set()
        self._update_schedule_thread.set()
        self._schedule_thread.join()
        self.logger.info("state active: stop_scheduler done")

    def on_exit(self):
        self._stop_scheduler()
        self.deactivate_runtime_on_request()
        self.deactivate_ping_on_request()
        self.deactivate_config_on_request()
        self.deactivate_end_on_request()
        self.deactivate_reonboarding_request()
        self.deactivate_receive_heartbeat()
        self.deactivate_forward_logger()
        self.logger.info("state on_exit: Active")

    def _enter_schedule(self, interval, function):
        if not self._stopping_schedule_thread:
            self._event_runtime = self._scheduler.enter(interval, 0, function)
            if not self._stop_schedule_thread:
                next_event = self._scheduler.run(blocking=False)
                self.logger.debug("state active: update schedule - now: {}, next in: {}s, queue: {}"
                                  .format(time(), next_event, self._scheduler.queue))
                self._update_schedule_thread.set()
        else:
            self.logger.debug("state active: _enter_schedule - skipped (_stop_schedule_thread is True)")

    def _schedule_event_runtime(self):
        if self.send_runtime_interval > 0:
            self.logger.info("state active: schedule runtime ({}s)".format(self.send_runtime_interval))
            self._enter_schedule(self.send_runtime_interval, self._execute_runtime)
        else:
            self.logger.info("state active: runtime not added to schedule (interval = 0s)")

    def _schedule_event_config(self):
        if self.send_config_interval > 0:
            self.logger.info("state active: schedule config ({}s)".format(self.send_config_interval))
            self._enter_schedule(self.send_config_interval, self._execute_config)
        else:
            self.logger.info("state active: config not added to schedule (interval = 0s)")

    def _schedule_event_ping(self):
        if self.send_ping_interval > 0:
            self.logger.info("state active: schedule ping ({}s)".format(self.send_ping_interval))
            self._enter_schedule(self.send_ping_interval, self._execute_ping)
        else:
            self.logger.info("state active: ping not added to schedule (interval = 0s)")

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

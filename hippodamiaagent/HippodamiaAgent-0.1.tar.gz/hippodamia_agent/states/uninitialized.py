from tantamount.astate import AState
from hippodamia_agent.states.event_ids import event_ids


class Uninitialized(AState):
    sigint = None
    update_uuid = None
    decativate_last_will = None
    logger = None

    def __init__(self, logger, sigint):
        AState.__init__(self)
        self.logger = logger
        self.sigint = sigint
        self.logger.info("State 'Uninitialized' created")

    def on_entry(self):
        self.logger.info("state on_entry: Uninitialized")
        if self.sigint.is_set():
            return event_ids.SIGINT

        self.update_uuid()
        self.decativate_last_will()

        return event_ids.NEW_UUID

    def on_exit(self):
        self.logger.info("state on_exit: Uninitialized")
        pass

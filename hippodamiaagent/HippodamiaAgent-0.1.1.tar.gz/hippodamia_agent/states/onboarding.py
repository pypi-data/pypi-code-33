from tantamount.astate import AState
from hippodamia_agent.states.event_ids import event_ids


class Onboarding(AState):
    sigint = None
    logger = None

    def __init__(self, logger, sigint):
        AState.__init__(self)
        self.sigint = sigint
        self.logger = logger
        self.logger.info("State 'Onboarding' created")

    def on_entry(self):
        self.logger.info("state on_entry: Onboarding")
        if self.sigint.is_set():
            return event_ids.SIGINT

        return None

    def on_exit(self):
        self.logger.info("state on_exit: Onboarding")
        pass

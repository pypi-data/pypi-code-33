from tantamount.astate import AState
from hippodamia_agent.states.event_ids import event_ids


class Initialized(AState):
    sigint = None
    activate_onboarding_response = None
    send_onboarding_request = None
    logger = None

    def __init__(self, logger, sigint):
        AState.__init__(self)
        self.logger = logger
        self.sigint = sigint
        self.logger.info("State 'Initialized' created")

    def on_entry(self):
        self.logger.info("state on_entry: Initialized")
        if self.sigint.is_set():
            return event_ids.SIGINT

        self.activate_onboarding_response()
        self.send_onboarding_request()

        return event_ids.ONBOARDING_REQUEST

    def on_exit(self):
        self.logger.info("state on_exit: Initialized")
        pass

from tantamount.astate import AState


class Terminating(AState):
    send_offboarding_message = None
    logger = None

    def __init__(self, logger):
        AState.__init__(self)
        self.logger = logger
        self.logger.info("State 'Terminating' created")

    def on_entry(self):
        self.logger.info("state on_entry: Terminating")
        self.send_offboarding_message()
        return None

    def on_exit(self):
        self.logger.info("state on_exit: Terminating")
        pass

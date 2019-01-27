class AState:
    def __init__(self):
        self.id = None
        self.groupid = None

    def on_entry(self):
        """
        called upon entry to this state. may return a event id that triggers a new state transistion immediately.

        :return: eventid or None
        """
        raise NotImplementedError

    def on_exit(self):
        raise NotImplementedError

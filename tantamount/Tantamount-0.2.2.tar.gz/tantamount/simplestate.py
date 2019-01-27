from tantamount.astate import AState
import time


class SimpleState(AState):
    def __init__(self):
        AState.__init__(self)

    def on_entry(self):
        pass

    def on_exit(self):
        pass

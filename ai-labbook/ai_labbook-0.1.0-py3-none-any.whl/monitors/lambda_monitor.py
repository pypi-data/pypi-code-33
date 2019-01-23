from labbook.monitors import Monitor
from labbook import ExpEvents

class LambdaMonitor(Monitor):
    def __init__(self, name, handle_fn, events=[], experiment=None):
        super(LambdaMonitor, self).__init__(name, events=events, experiment=experiment)
        self.handle_fn = handle_fn

    def __call__(self, *args, **kwargs):
        self.handle_fn(*args, **kwargs)

class Monitor(object):
    def __init__(self, name, events=[], experiment=None):
        self.name = name
        self.experiment = experiment
        self.events = events

        self._attach(self.experiment)

    def _attach(self, experiment):
        if experiment is not None:
            self.experiment = experiment
            self.experiment.register_monitor(self)

    def __call__(self, event, new_value, **kwargs):
        pass

    def state_dict(self):
        pass

    def load_state_dict(self, state_dict):
        pass


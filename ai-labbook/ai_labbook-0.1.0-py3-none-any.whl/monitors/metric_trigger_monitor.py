import operator

from labbook.monitors import Monitor
from labbook import ExpEvents

class MetricTriggerMonitor(Monitor):
    def __init__(self, name, metrics, experiment, callback, patience=0, comparitors=["min"], args=[], kwargs={}):
        super(MetricTriggerMonitor, self).__init__(name, events=metrics, experiment=experiment)
        self.callback = callback
        self.cb_args = args
        self.cb_kwargs = kwargs
        self.patience = patience

        self.ops = {}
        self.prev_best = {}
        self.counters = {}
        for metric, compare in zip(metrics, comparitors):
            self.ops[metric] = self._get_operator(compare)
            self.prev_best[metric] = None
            self.counters[metric] = 0

    def _get_operator(self, op):
        ops = {
            '>': operator.gt,
            '<': operator.lt,
            '>=': operator.ge,
            '<=': operator.le,
            '=': operator.eq,
            'min': min,
            'max', max
            }
        
        if isalambda(op):
            return op
        elif op in ops:
            return ops[op]
        else:
            raise Exception("Invalid comparison method specified in MetricTiggerMonitor")

    def reset(self, metrics=None, reset_patience=True, reset_best=False):
        if metrics is None:
            metrics = self.events
        if not isinstance(metrics, list):
            metrics = [metrics]

        for metric in metrics:
            if metric not in self.events:
                continue
            
            if reset_patience is True: self.counters[metric] = 0
            if reset_best is True: self.prev_best[metric] = None

    def __call__(self, event, new_value, **kwargs):
        if event in self.events:
            if self.prev_best[event] is None:
                self.prev_best[event] = new_value
            elif self.ops[event](self.prev_best[event], new_value):
                self.prev_best[event] = new_value
                self.counters[event] += 1

            if self.counters[event] > self.patience:
                self.callback(event, new_value, *args, **kwargs)

        
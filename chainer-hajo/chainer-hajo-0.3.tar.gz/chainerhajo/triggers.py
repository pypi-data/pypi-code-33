class SecondTrigger(object):
    def __init__(self, interval=30):
        self._next_time = interval
        self.interval = interval

    def __call__(self, trainer):
        if self._next_time < trainer.elapsed_time:
            self._next_time = trainer.elapsed_time+self.interval
            return True
        else:
            return False

    def serialize(self, serializer):
        self._next_time = serializer('next_time', self._next_time)

class MinuteTrigger(SecondTrigger):
    def __init__(self, interval=5):
        super(MinuteTrigger, self).__init__(60*interval)

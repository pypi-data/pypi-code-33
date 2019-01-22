import abc
import uuid


class Transfer():
    def __init__(self, log, source, target, config):
        self.id = uuid.uuid4()
        self.source = source
        self.target = target
        self.config = config
        self.log = log

    @abc.abstractmethod
    def run(self):
        pass

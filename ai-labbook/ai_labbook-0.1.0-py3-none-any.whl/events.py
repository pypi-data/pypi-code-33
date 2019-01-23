
class SimpleEventBus:
    def __init__(self):
        self.dispatcher = {}

    def subscribe(self, event, handler):
        if event not in self.dispatcher:
            self.dispatcher[event] = []
        
        self.dispatcher.append(handler)

    def unsubscribe(self, event, handler=None):
        if event in self.dispatcher:
            if handler is not None:
                self.dispatcher[event].remove(handler)
            else:
                del self.dispatcher[event]

    def emit(self, event, *args, **kwargs):
        if event in self.dispatcher:
            for handler in self.dispatcher[event]:
                handler(event, *args, **kwargs)

    def __len__(self):
        num_events = sum([len(v) for v in self.dispatcher.values()])
        return (len(self.dispatcher), num_events)
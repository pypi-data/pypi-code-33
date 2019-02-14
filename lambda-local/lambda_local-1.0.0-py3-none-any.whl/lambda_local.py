import json


class LambdaLocal:

    def __init__(self, func, events, context):
        self.func = func
        try:
            self.events = json.loads(events)
        except TypeError as te:
            self.events = json.loads(json.dumps(events))
        except Exception as e:
            raise Exception(e)
        self.context = context

    def run(self):
        try:
            self.func(self.events, self.context)
        except Exception as e:
            print(e)
            raise Exception(e)

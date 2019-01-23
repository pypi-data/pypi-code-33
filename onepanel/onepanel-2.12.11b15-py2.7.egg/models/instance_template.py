import json

class InstanceTemplate:
    def __init__(self):
        self.uid = None

    def api_json(self):
        return {
            'uid': self.uid
        }

def from_json(dct):
    template = InstanceTemplate()

    template.uid = dct['uid']

    return template

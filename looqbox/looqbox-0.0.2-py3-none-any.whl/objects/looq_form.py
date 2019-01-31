import json
from looqbox.objects.looq_object import LooqObject


class ObjForm(LooqObject):

    def __init__(self, title=None, method="GET", action=None, filepath=None, **fields):
        super().__init__()
        if action is None:
            action = ""
        self.title = title
        self.method = method
        self.action = action
        self.filepath = filepath
        self.fields = fields

    @property
    def to_json_structure(self):
        json_content = {"objectType": "form",
                        "title": [self.title],
                        "method": self.method,
                        "action": self.action,
                        "filepath": self.filepath,
                        "fields": self.fields
                        }

        # Transforming in JSON
        form_json = json.dumps(json_content, indent=1)

        return form_json

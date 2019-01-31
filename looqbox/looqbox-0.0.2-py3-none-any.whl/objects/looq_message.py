from looqbox.objects.looq_object import LooqObject
import json


class ObjMessage(LooqObject):

    def __init__(self, text, type="alert-default", align="center", style=None):
        super().__init__()
        if style is None:
            style = {}
        self.text = text
        self.text_type = type
        self.text_align = align
        self.text_style = style

    @property
    def to_json_structure(self):
        json_content = {'objectType': 'message',
                        'text': [self.text],
                        'type': self.text_type,
                        'style': {"text-align": [self.text_align]}
                        }

        # Adding the dynamic style parameters
        for style in list(self.text_style.keys()):
            json_content['style'].setdefault(style, []).append(self.text_style[style])

        # Transforming in JSON
        message_json = json.dumps(json_content, sort_keys=True, indent=1)

        return message_json

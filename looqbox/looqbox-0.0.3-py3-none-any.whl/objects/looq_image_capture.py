import json
import os
import shutil
from looqbox.objects.looq_object import LooqObject
from looqbox.global_calling import GlobalCalling


class ObjImageCapture(LooqObject):

    def __init__(self, filepath, title=None, content=None):
        super().__init__()
        if content is None:
            content = []
        if title is None:
            title = ""
        self.filepath = filepath
        self.title = title
        self.content = content

    @property
    def to_json_structure(self):

        json_content = {"objectType": "imageCapture",
                        "title": self.title,
                        "content": self.content,
                        "filepath": self.filepath
                        }

        # Transforming in JSON
        image_capture = json.dumps(json_content, indent=1)

        return image_capture

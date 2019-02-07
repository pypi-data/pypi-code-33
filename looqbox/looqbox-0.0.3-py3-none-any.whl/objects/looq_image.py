import json
import os
import shutil
from looqbox.objects.looq_object import LooqObject
from looqbox.global_calling import GlobalCalling


class ObjImage(LooqObject):

    def __init__(self, src, width=None, height=None, style=None, tooltip=None, link=None):
        super().__init__()
        if link is None:
            link = {}
        if tooltip is None:
            tooltip = {}
        if style is None:
            style = []
        self.source = src
        self.width = width
        self.height = height
        self.style = style
        self.tooltip = tooltip
        self.link = link

    @property
    def to_json_structure(self):
        source = self.source
        if 'https://' not in self.source:
            # From global variable looq
            if os.path.dirname(self.source) == GlobalCalling.looq.temp_dir:
                source = "/api/tmp/download/" + os.path.basename(self.source)
            else:
                template_file = os.path.join(GlobalCalling.looq.response_dir() + "/" + self.source)
                temporary_file = GlobalCalling.looq.temp_file(self.source)
                shutil.copy(template_file, temporary_file)
                source = "/api/tmp/download/" + os.path.basename(temporary_file)

        width_array = [str(self.width)]
        height_array = [str(self.height)]

        json_content = {"objectType": "image",
                        "src": source,
                        "style": {
                            "width": width_array,
                            "height": height_array,
                        },
                        "link": self.link,
                        "tooltip": self.tooltip
                        }

        # Transforming in JSON
        image_json = json.dumps(json_content, indent=1)

        return image_json

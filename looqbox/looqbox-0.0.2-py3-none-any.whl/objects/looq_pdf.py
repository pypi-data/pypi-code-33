import json
import os
import shutil
from looqbox.objects.looq_object import LooqObject
from looqbox.global_calling import GlobalCalling


class ObjPDF(LooqObject):

    def __init__(self, src, initial_page=1, height=None):
        super().__init__()
        self.source = src
        self.initial_page = initial_page
        self.height = height

    @property
    def to_json_structure(self):

        if 'https://' not in self.source:
            # From global variable looq
            if os.path.dirname(self.source) == GlobalCalling.looq.temp_dir:
                self.source = "/api/tmp/download" + os.path.basename(self.source)
            else:
                template_file = os.path.join(GlobalCalling.looq.response_dir() + "/" + self.source)
                temporary_file = GlobalCalling.looq.temp_file(self.source)
                shutil.copy(template_file, temporary_file)
                self.source = "/api/tmp/download" + os.path.basename(temporary_file)

        height_array = [str(self.height)]

        json_content = {"objectType": "pdf",
                        "src": self.source,
                        "style": {
                            "height": height_array,
                        },
                        "initialPage": self.initial_page,
                        }

        # Transforming in JSON
        pdf_json = json.dumps(json_content, indent=1)

        return pdf_json

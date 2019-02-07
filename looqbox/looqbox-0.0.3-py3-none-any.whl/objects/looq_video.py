import json
import os
import shutil
from looqbox.objects.looq_object import LooqObject
from looqbox.global_calling import GlobalCalling


class ObjVideo(LooqObject):

    def __init__(self, src, auto_play=False):
        super().__init__()
        self.source = src
        self.auto_play = auto_play

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

        json_content = {"objectType": "video",
                        "src": source,
                        "autoPlay": self.auto_play
                        }

        # Transforming in JSON
        video_json = json.dumps(json_content, indent=1)

        return video_json

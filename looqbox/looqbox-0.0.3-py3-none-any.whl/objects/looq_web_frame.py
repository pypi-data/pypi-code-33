from looqbox.objects.looq_object import LooqObject
import json


class ObjWebFrame(LooqObject):

    def __init__(self, src, width=None, height=500, enable_fullscreen=False, open_fullscreen=False):
        super().__init__()
        self.source = src
        self.width = width
        self.height = height
        self.enable_fullscreen = enable_fullscreen
        self.open_fullscreen = open_fullscreen

    @property
    def to_json_structure(self):

        if self.width is None:
            self.width = ""
        else:
            self.width = str(self.width)

        json_content = {"objectType": "webframe",
                        "src": self.source,
                        "style": {
                            "width": str(self.width),
                            "height": str(self.height)
                        },
                        "enableFullscreen": self.enable_fullscreen,
                        "openFullscreen": self.open_fullscreen,
                        }

        # Transforming in JSON
        web_frame_json = json.dumps(json_content, indent=1)

        return web_frame_json

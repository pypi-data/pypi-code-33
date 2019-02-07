import json
from typing import List, Any

from looqbox.objects.looq_object import LooqObject


class ResponseFrame(LooqObject):
    """
    Content: LooqObjects that will be inside the frame
    Class: Class of the Looqbox Frame
    Style: A lista of CSS styles to change the Frame appearance (List)
    Stacked: Define if the frames will be stacked inside the board
    Title: Title of the frame (String)
    """

    def __init__(self, content=None, frame_class=None, style=None, stacked=True, title=None):
        super().__init__()
        if frame_class is None:
            frame_class = []
        if content is None:
            content = []
        if title is None:
            title = []
        if style is None:
            style = {}

        self.content = content
        self.frame_class = frame_class
        self.style = style
        self.stacked = stacked
        self.title = title

    @property
    def to_json_structure(self):
        # Dynamic error message to help the users to understand the error
        if type(self.content) is not list:
            raise TypeError("Content is not a list")

        objects_json_list = [json.loads(looq_object.to_json_structure) for looq_object in
                             self.content if looq_object is not None]

        json_content = {'type': 'frame',
                        'class': self.frame_class,
                        'style': self.style,
                        'stacked': self.stacked,
                        'title': self.title,
                        'content': objects_json_list
                        }

        # Transforming in JSON
        frame_json = json.dumps(json_content, indent=1)

        return frame_json

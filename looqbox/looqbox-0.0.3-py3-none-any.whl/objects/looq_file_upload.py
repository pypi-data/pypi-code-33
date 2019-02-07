from looqbox.objects.looq_object import LooqObject
import json


class ObjFileUpload(LooqObject):
    """
    This object create a view to drag and drop a file that will be read and used in other script of the response.
    """
    def __init__(self, filepath, title=None, content=None):
        super().__init__()
        if title is None:
            title = []
        if content is None:
            content = []
        self.filepath = filepath
        self.title = title
        self.content = content

    @property
    def to_json_structure(self):

        json_content = {"objectType": "fileUpload",
                        "title": self.title,
                        "content": self.content,
                        "filepath": self.filepath
                        }

        # Transforming in JSON
        file_upload_json = json.dumps(json_content, indent=1)

        return file_upload_json

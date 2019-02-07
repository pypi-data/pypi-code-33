from looqbox.objects.looq_object import LooqObject
import json


class ObjHTML(LooqObject):
    """
    This class get a HTML and wrap it in a Looqbox object to be used inside the interface

    Example:
        HTML = ObjHTML("<div> Hello Worlds </div>)

    Attributes:
        html (str): Is the html code that will be wrapped
    """
    def __init__(self, html):
        super().__init__()
        self.html = html

    @property
    def to_json_structure(self):
        json_content = {"objectType": "html",
                        "html": self.html
                        }

        # Transforming in JSON
        html_json = json.dumps(json_content, indent=1)

        return html_json

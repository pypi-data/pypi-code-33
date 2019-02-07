from looqbox.objects.looq_object import LooqObject
import json


class ObjEmbed(LooqObject):
    """
    Return a frame inside Looqbox interface using as source an iframe HTML tag

    Attributes:
        iframe: String = Embedded element dimensions and source in HTML format

        Examples:
            webframe0 = ObjEmbec( "<iframe frameborder=\"0\" width=\"560\" height=\"315\"
             src=\"https://app.biteable.com/watch/embed/looqbox-presentation-1114895\">
           </iframe>")
           
        :return A Looqbox ObjEmbed object
    """
    def __init__(self, iframe):
        super().__init__()
        self.iframe = iframe

    @property
    def to_json_structure(self):

        json_content = {"objectType": "embed",
                        "iframe": self.iframe
                        }

        # Transforming in JSON
        embed = json.dumps(json_content, indent=1)

        return embed

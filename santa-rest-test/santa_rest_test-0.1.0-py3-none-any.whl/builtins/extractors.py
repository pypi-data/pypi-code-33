from jq import jq

from santa.parser import StringField
from santa.extractor import Extractor

from .fields import ContextValueField


class JQExtractor(Extractor):
    """
    Extract a jq pattern.
    """

    __yaml_name__ = "jq"
    pattern = StringField()
    bind = ContextValueField()

    async def __call__(self, response, ctx):
        data = jq(self.pattern).transform(await response.json())
        ctx.bind(self.bind, data, create=True)

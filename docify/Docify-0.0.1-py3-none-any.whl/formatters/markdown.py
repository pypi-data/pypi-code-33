from docify import Document
from docify.lib.formatter import Formatter


DOC_TMPL = '''\
{}


<sup>Generated using [Docify](https://github.com/rapidstack/docify)</sup>
'''

class Markdown(Formatter):
    handlers = {
        Document: lambda x: DOC_TMPL.format(x)
    }

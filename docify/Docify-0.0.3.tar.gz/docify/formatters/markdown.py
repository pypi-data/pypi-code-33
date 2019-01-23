from docify import Document
from docify.lib.formatter import Formatter


DOC_TMPL = '''\
{}


This document is generated using [Docify](https://github.com/rapidstack/docify)
'''


class Markdown(Formatter):
    '''Markdown formatter.
    By default Document object becomes markdown text when casted into string.
    So it's basically doing noting except adding a grumpy citation.
    '''
    handlers = {
        Document: lambda x: DOC_TMPL.format(x)
    }

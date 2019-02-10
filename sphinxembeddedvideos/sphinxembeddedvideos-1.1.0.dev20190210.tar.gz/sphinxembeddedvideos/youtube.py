from __future__ import division

import re
from docutils import nodes

from .common import css
from .common import EmbeddedVideo
from .common import visit_embedded_node


class youtube(nodes.General, nodes.Element):
    pass


def depart_youtube_node(self, node):
    pass


def visit_youtube_node(self, node):
    visit_embedded_node(
        self,
        node,
        alias="youtube",
        url="https://www.youtube.com/embed/%s",
        control_height=30,
    )


def visit_youtube_node_latex(self,node):
    self.body.append(r'\begin{quote}\begin{center}\fbox{\url{https://www.youtu.be/%s}}\end{center}\end{quote}'%node['id'])


class YouTube(EmbeddedVideo):
    embeddedfunction = youtube


def unsupported_visit_youtube(self, node):
    self.builder.warn('youtube: unsupported output format (node skipped)')
    raise nodes.SkipNode


def setup(app):
    node_visitors = {
        'html': (visit_youtube_node, depart_youtube_node),
        'latex': (visit_youtube_node_latex, depart_youtube_node),
        'man': (unsupported_visit_youtube, None),
        'texinfo': (unsupported_visit_youtube, None),
        'text': (unsupported_visit_youtube, None)
    }
    app.add_node(youtube, **node_visitors)
    app.add_directive("youtube", YouTube)

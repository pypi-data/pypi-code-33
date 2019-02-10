from __future__ import division

import re
from docutils import nodes

from .common import css
from .common import EmbeddedVideo
from .common import visit_embedded_node


class peertube(nodes.General, nodes.Element):
    pass


def depart_peertube_node(self, node):
    pass


def visit_peertube_node(self, node):
    visit_embedded_node(
        self,
        node,
        alias="peertube",
        url="https://peertube.social/videos/embed/%s",
        control_height=0,
    )


def visit_peertube_node_latex(self,node):
    self.body.append(r'\begin{quote}\begin{center}\fbox{\url{https://www.youtu.be/%s}}\end{center}\end{quote}'%node['id'])


class PeerTube(EmbeddedVideo):
    embeddedfunction = peertube


def unsupported_visit_peertube(self, node):
    self.builder.warn('peertube: unsupported output format (node skipped)')
    raise nodes.SkipNode


def setup(app):
    node_visitors = {
        'html': (visit_peertube_node, depart_peertube_node),
        'latex': (visit_peertube_node_latex, depart_peertube_node),
        'man': (unsupported_visit_peertube, None),
        'texinfo': (unsupported_visit_peertube, None),
        'text': (unsupported_visit_peertube, None)
    }
    app.add_node(peertube, **node_visitors)
    app.add_directive("peertube", PeerTube)

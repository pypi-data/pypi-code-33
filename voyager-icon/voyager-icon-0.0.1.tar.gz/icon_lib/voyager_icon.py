import os
# import logging

from jinja2 import nodes
from jinja2.ext import Extension

# logger = logging.getLogger('tornado.general')

class VoyagerIcon(Extension):
    tags = {"vgicon"}

    def __init__(self, environment):
        super(VoyagerIcon, self).__init__(environment)

        # add the defaults to the environment
        environment.extend(width=16,height=16)

    def parse(self, parser):
        lineno = next(parser.stream).lineno

        # Parse icon name
        args = [parser.parse_expression()]

        # Parse icon width 
        if parser.stream.skip_if('comma'):
            args.append(parser.parse_expression())
        else:
            args.append(nodes.Const(None))

        # Parse icon height
        if parser.stream.skip_if('comma'):
            args.append(parser.parse_expression())
        else:
            args.append(nodes.Const(None))

        return nodes.CallBlock(
            self.call_method('_render', args),
            [], [], [], lineno=lineno)

    def _render(self, name, width, height, caller):
        # Set width from defaults if empty
        if width is None:
            width = self.environment.width

        # Set height from defaults if empty
        if height is None:
            height = self.environment.height

        # Build path to the icon SVG file
        path = os.path.join(os.path.dirname(__file__), 'icons', name + '.svg')

        # Check if file exists and return warning if it doesn't exist
        if os.path.isfile(path):
            svg = open(path, 'r').read()
            return svg.replace('{WIDTH}', str(width)).replace('{HEIGHT}', str(height))
        else:
            return 'vgicon: unknown icon ' + name
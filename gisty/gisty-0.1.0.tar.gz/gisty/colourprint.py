import sys


class ColourPrint:

    def __init__(self, colour):
        self.colour = colour


    def print(self, template: str, **kwargs):
        if self.colour and 'colour' in kwargs:
            template = '{colour}' + template
        msg = template.format(**kwargs)
        if 'error' in kwargs:
            print(msg, file=sys.stderr)
        else:
            print(msg)

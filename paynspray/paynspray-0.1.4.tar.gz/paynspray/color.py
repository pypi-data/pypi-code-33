from __future__ import print_function
import copy, re, string

AnsiAttributes = {
    'clear': 0,
    'reset': 0,
    'bold': 1,
    'dark': 2,
    'underline': 4,
    'underscore': 4,
    'blink': 5,
    'reverse': 7,
    'concealed': 8,
    'black': 30,
    'red': 31,
    'green': 32,
    'yellow': 33,
    'blue': 34,
    'magenta': 35,
    'cyan': 36,
    'white': 37,
    'on_black': 40,
    'on_red': 41,
    'on_green': 42,
    'on_yellow': 43,
    'on_blue': 44,
    'on_magenta': 45,
    'on_cyan': 46,
    'on_white': 47,
}

class UiColor(object):
    """Mixin that provides access to functions related to color output"""
    # A class that inherits UiColor must implement the following methods:
    #
    # print - function that outputs text to an underlying stream
    # supports_color - property (bool) that returns if the stream supports color
    #

    def __init__(self, *args, **kwargs):
        pass

    def ansi(self, *args):
        global AnsiAttributes
        attr = ";".join(map(str, [AnsiAttributes[x] for x in args]))
        if len(attr) != 0:
            attr = "\x1B[{}m".format(attr)
        return attr

    def colorize(self, *args):
        try:
            if self.supports_color == True:
                return self.ansi(*args)
            else:
                return ''
        except Exception as e:
            return ''

    def substitute_colors(self, msg, in_prompt = None):
        _str = copy.copy(msg)
        pre_color = post_color = ''
        if (in_prompt):
            pre_color = "\x01"
            post_color = "\x02"
        _str = re.sub(r'%cya', pre_color + self.colorize('cyan') + post_color, _str)
        _str = re.sub(r'%red', pre_color + self.colorize('red') + post_color, _str)
        _str = re.sub(r'%grn', pre_color + self.colorize('green') + post_color, _str)
        _str = re.sub(r'%blu', pre_color + self.colorize('blue') + post_color, _str)
        _str = re.sub(r'%yel', pre_color + self.colorize('yellow') + post_color, _str)
        _str = re.sub(r'%whi', pre_color + self.colorize('white') + post_color, _str)
        _str = re.sub(r'%mag', pre_color + self.colorize('magenta') + post_color, _str)
        _str = re.sub(r'%blk', pre_color + self.colorize('black') + post_color, _str)
        _str = re.sub(r'%dred', pre_color + self.colorize('dark','red') + post_color, _str)
        _str = re.sub(r'%dgrn', pre_color + self.colorize('dark','green') + post_color, _str)
        _str = re.sub(r'%dblu', pre_color + self.colorize('dark','blue') + post_color, _str)
        _str = re.sub(r'%dyel', pre_color + self.colorize('dark','yellow') + post_color, _str)
        _str = re.sub(r'%dcya', pre_color + self.colorize('dark','cyan') + post_color, _str)
        _str = re.sub(r'%dwhi', pre_color + self.colorize('dark','white') + post_color, _str)
        _str = re.sub(r'%dmag', pre_color + self.colorize('dark','magenta') + post_color, _str)
        _str = re.sub(r'%und', pre_color + self.colorize('underline') + post_color, _str)
        _str = re.sub(r'%bld', pre_color + self.colorize('bold') + post_color, _str)
        _str = re.sub(r'%clr', pre_color + self.colorize('clear') + post_color, _str)
        _str = re.sub(r'%bgblu', pre_color + self.colorize('on_blue') + post_color, _str)
        _str = re.sub(r'%bgyel', pre_color + self.colorize('on_yellow') + post_color, _str)
        _str = re.sub(r'%bggrn', pre_color + self.colorize('on_green') + post_color, _str)
        _str = re.sub(r'%bgmag', pre_color + self.colorize('on_magenta') + post_color, _str)
        _str = re.sub(r'%bgblk', pre_color + self.colorize('on_black') + post_color, _str)
        _str = re.sub(r'%bgred', pre_color + self.colorize('on_red') + post_color, _str)
        _str = re.sub(r'%bgcyn', pre_color + self.colorize('on_cyan') + post_color, _str)
        _str = re.sub(r'%bgwhi', pre_color + self.colorize('on_white') + post_color, _str)

        return _str

    def reset_color(self):
        if not self.supports_color:
            return
            
        self.print(self.colorize('clear'))

    def do_colorize(self, *args):
        try:
            if self.supports_color == True:
                return self.ansi(*args)
            else:
                return ''
        except Exception as e:
            return ''



















#! /usr/local/bin/python3
# encoding: utf-8

# 引入该函数，为了解决低版本中print(end=)参数不支持的问题
from __future__ import print_function

# -----------------------------------------------------------------------------------
#   显示格式: \033[显示方式;前景色;背景色m
#   只写一个数字代表前景色
# -----------------------------------------------------------------------------------


LTCSI = '\033['


def code_to_chars(code):
    return LTCSI + str(code) + 'm'


class LTCodes(object):
    def __init__(self):
        # the subclasses declare class attributes which are numbers.
        # Upon instantiation we define instance attributes, which are the same
        # as the class attributes but wrapped with the ANSI escape sequence
        for name in dir(self):
            if not name.startswith('_'):
                value = getattr(self, name)
                setattr(self, name, code_to_chars(value))


class LTFore(LTCodes):
    BLACK           = 30
    RED             = 31
    GREEN           = 32
    YELLOW          = 33
    BLUE            = 34
    MAGENTA         = 35
    CYAN            = 36
    WHITE           = 37
    RESET           = 39


class LTBack(LTCodes):
    BLACK           = 40
    RED             = 41
    GREEN           = 42
    YELLOW          = 43
    BLUE            = 44
    MAGENTA         = 45
    CYAN            = 46
    WHITE           = 47
    RESET           = 49


class LTStyle(LTCodes):
    HIGHLIGHTED = 1   # 高亮
    UNDERLINE   = 4   # 下划线
    BLINK       = 5   # 目前尝试仅在terminal下有效果，iTerm2下无效
    INVISIBLE   = 8   # 目前尝试仅在terminal下有效果，iTerm2下无效
    RESET_ALL   = 0   # 重置


kFore  = LTFore()
kBack  = LTBack()
kStyle = LTStyle()


class PrintWithColor:

    """
        def __init__(self):
        for name in dir(self):
            print('---v---'+name)
            if name.startswith('fore_'):
                pass
            elif name.startswith('back_'):
                pass
            elif name.startswith('style_'):
                pass
            else:
                pass
    """

    # --------------------------------------------------------------------------
    # A. simple foreground color.
    # e.g.
    #       PrintWithColor.cyan('match')
    #       PrintWithColor.red(['1', '2'], end=' ').cyan('abcde')
    # --------------------------------------------------------------------------

    @classmethod
    def __simple_print(cls, color, v, end):
        print(f'{color}{v}{kFore.RESET}', end=end)
        return cls

    @classmethod
    def black(cls, v, end='\n'):
        return cls.__simple_print(kFore.BLACK, v, end)

    @classmethod
    def red(cls, v, end='\n'):
        return cls.__simple_print(kFore.RED, v, end)

    @classmethod
    def green(cls, v, end='\n'):
        return cls.__simple_print(kFore.GREEN, v, end)

    @classmethod
    def yellow(cls, v, end='\n'):
        return cls.__simple_print(kFore.YELLOW, v, end)

    @classmethod
    def blue(cls, v, end='\n'):
        return cls.__simple_print(kFore.BLUE, v, end)

    @classmethod
    def magenta(cls, v, end='\n'):
        return cls.__simple_print(kFore.MAGENTA, v, end)

    @classmethod
    def cyan(cls, v, end='\n'):
        return cls.__simple_print(kFore.CYAN, v, end)

    @classmethod
    def white(cls, v, end='\n'):
        return cls.__simple_print(kFore.WHITE, v, end)

    # --------------------------------------------------------------------------
    #  B. advanced chain (foreground color, background color, style)
    #  e.g.
    #       PrintWithColor.fore_cyan().style_blink().back_red().apply('match')
    #       PrintWithColor.green('ge', end=' ').back_white().fore_black().apply('高级链', end=' ').red('red')
    # --------------------------------------------------------------------------

    __saved_chain = ''

    @classmethod
    def __advanced_chain(cls, node):
        cls.__saved_chain += node
        return cls

    # -------- foreground color --------

    @classmethod
    def fore_black(cls):
        return cls.__advanced_chain(kFore.BLACK)

    @classmethod
    def fore_red(cls):
        return cls.__advanced_chain(kFore.RED)

    @classmethod
    def fore_green(cls):
        return cls.__advanced_chain(kFore.GREEN)

    @classmethod
    def fore_yellow(cls):
        return cls.__advanced_chain(kFore.YELLOW)

    @classmethod
    def fore_blue(cls):
        return cls.__advanced_chain(kFore.BLUE)

    @classmethod
    def fore_magenta(cls):
        return cls.__advanced_chain(kFore.MAGENTA)

    @classmethod
    def fore_cyan(cls):
        return cls.__advanced_chain(kFore.CYAN)

    @classmethod
    def fore_white(cls):
        return cls.__advanced_chain(kFore.WHITE)

    # -------- background color --------

    @classmethod
    def back_black(cls):
        return cls.__advanced_chain(kBack.BLACK)

    @classmethod
    def back_red(cls):
        return cls.__advanced_chain(kBack.RED)

    @classmethod
    def back_green(cls):
        return cls.__advanced_chain(kBack.GREEN)

    @classmethod
    def back_yellow(cls):
        return cls.__advanced_chain(kBack.YELLOW)

    @classmethod
    def back_blue(cls):
        return cls.__advanced_chain(kBack.BLUE)

    @classmethod
    def back_magenta(cls):
        return cls.__advanced_chain(kBack.MAGENTA)

    @classmethod
    def back_cyan(cls):
        return cls.__advanced_chain(kBack.CYAN)

    @classmethod
    def back_white(cls):
        return cls.__advanced_chain(kBack.WHITE)

    # -------- style --------

    @classmethod
    def style_highlight(cls):
        return cls.__advanced_chain(kStyle.HIGHLIGHTED)

    @classmethod
    def style_underline(cls):
        return cls.__advanced_chain(kStyle.UNDERLINE)

    @classmethod
    def style_blink(cls):
        return cls.__advanced_chain(kStyle.BLINK)

    @classmethod
    def style_invisible(cls):
        return cls.__advanced_chain(kStyle.INVISIBLE)

    # -------- apply --------
    @classmethod
    def apply(cls, v, end='\n'):
        print(f'{cls.__saved_chain}{v}{kFore.RESET}{kBack.RESET}{kStyle.RESET_ALL}', end=end)
        cls.clear()
        return cls

    # -------- clear --------

    @classmethod
    def clear(cls):
        cls.__saved_chain = ''


# TEST
# PrintWithColor.cyan(['1', '2'])
# PrintWithColor.red(['1', '2'], end=' ').cyan('abcde')
# PrintWithColor.fore_green().style_blink().back_cyan().apply(['a', 'b', 'c'])

# PrintWithColor.green('ge', end=' ').back_white().fore_black().apply('高级链', end=' ').red('red')
#coding=utf-8
import _curses, curses
import time
import re
import colour_helpers
from contextlib import contextmanager

import colored
from colored import stylize

import locale
locale.setlocale(locale.LC_ALL, '')
pref_encoding = locale.getpreferredencoding()

@contextmanager
def curses_screen():
    screen = curses.initscr()
    try:
        curses.start_color()
        curses.curs_set(0)
        curses.noecho()
        curses.cbreak()
        yield screen
    finally:
        curses.endwin()

def colour_styled(string, hex_col):
    return stylize(string, colored.fg(colour_helpers.term_col_to_hex(colour_helpers.get_closest_term_colour(hex_col))))

class TerminalTable(object):
    DEFAULT_STYLE = {
        'table': (
            (u'╔', u'═', u'╦', u'╗'),
            (u'╠', u'═', u'╬', u'╣'),
            (u'╚', u'═', u'╩', u'╝'),
            (u'║', u' ', u'║', u'║')
        ),
        'danger_selected': '#990000BB'.lower(),
        'selected': '#444444AA'.lower(),
        'highlighted': '#0000FF88'.lower(),
    }
    COL_REG = re.compile(r'<colou?r (#[0-9a-f]{6})>((?:(?!<\/colou?r>).)*)(:?</colou?r>)?')
    # find all these, and replace them with either their group 2 match, or not, or whatev
    def __init__(self, columns, rows, style=None, padding=None):
        self._style = style or self.DEFAULT_STYLE
        self._padding = padding or (1, 0)
        self._columns = [str(col) for col in columns]
        self._rows = [[str(comp) for comp in row] for row in rows]
        self._num_rows = len(rows)
        self._num_cols = len(columns)

        self._column_widths = []
        members = [self._columns] + self._rows
        for i in xrange(len(columns)):
            self._column_widths.append(max(self._formatted_width(m[i]) for m in members))

    def _parse_colour(self, string):
        components = []
        while string:
            match = self.COL_REG.search(string)
            if not match:
                components.append((string, None))
                return components
            if match.start() > 0:
                components.append((string[:match.start()], None))
            components.append((match.groups()[1], match.groups()[0]))
            string = string[match.end():]
        return components

    def _formatted_width(self, string):
        components = self._parse_colour(string)
        l = sum(len(c[0]) for c in components)
        return l + (self._padding[0] * 2)

    def _strip_format(self, string):
        components = self._parse_colour(string)
        return ''.join(c[0] for c in components)

    def _colour_format(self, string):
        components = self._parse_colour(string)
        return ''.join(colour_styled(c[0], c[1]) if c[1] else c[0] for c in components)

    def _stripped_len_diff(self, string):
        stripped = self._strip_format(string)
        coloured = self._colour_format(string)
        return len(coloured) - len(stripped)

    def _get_row(self, row_style, contents=None, centered=False, coloured=True):
        if not contents:
            column_strs = row_style[2].join(row_style[1] * width for width in self._column_widths)
        else:
            pad = ' ' * self._padding[0]
            if coloured:
                if centered:
                    column_strs = row_style[2].join(pad + self._colour_format(c).center(self._stripped_len_diff(c) + self._column_widths[i] - (self._padding[0] * 2)) + pad for i, c in enumerate(contents))
                else:
                    column_strs = row_style[2].join(pad + self._colour_format(c).ljust(self._stripped_len_diff(c) + self._column_widths[i] - (self._padding[0] * 2)) + pad for i, c in enumerate(contents))
            else:
                if centered:
                    column_strs = row_style[2].join(pad + self._strip_format(c).center(self._column_widths[i] - (self._padding[0] * 2)) + pad for i, c in enumerate(contents))
                else:
                    column_strs = row_style[2].join(pad + self._strip_format(c).ljust(self._column_widths[i] - (self._padding[0] * 2)) + pad for i, c in enumerate(contents))
        return (row_style[0] + column_strs + row_style[3])

    def show(self):
        t_style = self._style['table']
        print self._get_row(t_style[0])
        print self._get_row(t_style[3], self._columns, centered=True)
        print self._get_row(t_style[1])

        for i in xrange(self._num_rows):
            print self._get_row(t_style[3], self._rows[i])
        print self._get_row(t_style[2])

    def prompt_selection(self, prompt, multi_select=False, danger=False):
        if not self._rows:
            raise Exception('Can\'t select from 0 rows')
        try:
            with curses_screen() as screen:
                self._screen = screen
                self._danger = danger
                self._ypos = 0
                self._xpos = 0
                self._multi_select = multi_select
                self._cursor_index = 0
                self._selections = set()
                self._colour_pair = 1
                self._colour_pairs = {}
                self._parsed_rows = [[self._parse_colour(r) for r in row] for row in self._rows]

                def curses_colour(hex_col):
                    return colour_helpers.get_closest_term_colour(hex_col)

                def curses_colour_pair(fg_hex_col, bg_hex_col):
                    c1 = curses_colour(fg_hex_col)
                    c2 = curses_colour(bg_hex_col)
                    if c1 not in self._colour_pairs:
                        self._colour_pairs[c1] = {}
                    if c2 not in self._colour_pairs[c1]:
                        curses.init_pair(self._colour_pair, c1, c2)
                        self._colour_pairs[c1][c2] = self._colour_pair
                        self._colour_pair += 1

                    return self._colour_pairs[c1][c2]

                def render_row(parsed_components, selected=False, highlighted=False):
                    start_pos = self._xpos
                    def push_str(string, fg=None, bg=None):
                        if not string:
                            return
                        if fg == None:
                            fg = '#ffffff'
                        if bg == None:
                            bg = '#000000'
                        self._screen.addstr(self._ypos, self._xpos, string.encode(pref_encoding), curses.color_pair(curses_colour_pair(colour_helpers.blend_colours(fg, bg), bg)))
                        self._xpos = self._xpos + len(string)

                    if selected and highlighted:
                        bg = colour_helpers.blend_colours(self._style['highlighted'], self._style['danger_selected' if self._danger else 'selected'])
                    elif selected:
                        bg = self._style['danger_selected' if self._danger else 'selected']
                    elif highlighted:
                        bg = self._style['highlighted']
                    else:
                        bg = '#000000'

                    bg = colour_helpers.blend_colours(bg, '#000000')

                    t_style = self._style['table']
                    push_str(t_style[3][0], None, None)
                    for i, component in enumerate(parsed_components):
                        push_str(' ' * self._padding[0], None, bg)
                        stripped_width = 0
                        for part in component:
                            stripped_width += len(part[0])
                            push_str(part[0], part[1], bg)
                        push_str(' ' * (self._column_widths[i] - self._padding[0] - stripped_width), None, bg)

                        if i < self._num_cols - 1:
                            push_str(t_style[3][2], None, bg)

                    push_str(t_style[3][3], None, None)
                    self._xpos = start_pos

                def render():
                    t_style = self._style['table']
                    if self._cursor_index < 0:
                        self._cursor_index += self._num_rows
                    if self._cursor_index >= self._num_rows:
                        self._cursor_index -= self._num_rows

                    self._ypos = 0
                    def push_row(string):
                        self._screen.addstr(self._ypos, 0, string.encode(pref_encoding))
                        self._ypos += 1
                    push_row(prompt)
                    push_row(self._get_row(t_style[0], coloured=False))
                    push_row(self._get_row(t_style[3], self._columns, centered=True, coloured=False))
                    push_row(self._get_row(t_style[1], coloured=False))
                    for i in xrange(len(self._parsed_rows)):
                        render_row(self._parsed_rows[i], selected=i in self._selections, highlighted=i == self._cursor_index)
                        self._ypos += 1
                    push_row(self._get_row(t_style[2], coloured=False))
                    self._screen.refresh()

                def cursor_up():
                    self._cursor_index -= 1

                def cursor_down():
                    self._cursor_index += 1

                def select():
                    if self._multi_select:
                        if self._cursor_index in self._selections:
                            self._selections.remove(self._cursor_index)
                        else:
                            self._selections.add(self._cursor_index)

                render()
                while True:
                    key = self._screen.getch()
                    if key == 10:
                        # Enter
                        if self._multi_select:
                            return list(self._selections)
                        else:
                            return self._cursor_index
                    if key == 113:
                        # q
                        return None
                    elif key == 65:
                        # Up
                        cursor_up()
                    elif key == 66:
                        # Down
                        cursor_down()
                    elif key == 32:
                        # Space
                        select()
                    render()
        except KeyboardInterrupt:
            return None

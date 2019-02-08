from math import sqrt
from tkinter import Toplevel, TclError, Label, LEFT, SOLID

from cmax.common import igrid, jgrid, ijgrid, get_label, DEFAULT_FONT, RIGHT_CLICK, \
    BLACK, BROWN, RED, ORANGE, YELLOW, GREEN, BLUE, VIOLET, GRAY, WHITE, BODY, CYAN

COLORS = [BLACK, BROWN, RED, ORANGE, YELLOW, GREEN, BLUE, VIOLET, GRAY, WHITE]  # Resistor and wire colors
PREFIXES = ['sh', 'sv', 'lh', 'lv', 'op', 'po', 'mo', 'ro', 'he', 'pw', 'gd', 'pp', 'np', 'wi']  # Component labels


# A generic component
class Component:
    def __init__(self, ui, dynamic=True):
        self.ui = ui
        self.dynamic = dynamic
        self.highlighted = False
        self.x = self.y = 0
        self.moving = False

    def erase(self):
        for p in self.parts:
            self.canvas.delete(p)
        self.highlighted = False
        self.hide_tooltip()

    def move(self, dx, dy):
        if dx != 0 or dy != 0:  # Only move for nonzero deltas
            self.x += dx
            self.y += dy
            for p in self.parts:
                self.canvas.move(p, dx, dy)
                self.canvas.lift(p)

    def show_tooltip(self, event):
        pass

    def hide_tooltip(self, event=None):
        pass

    def highlight(self):
        if not self.highlighted:
            bbox = self.canvas.bbox(self.label)
            self.parts.append(self.canvas.create_rectangle(*bbox, outline=RED, fill=None, width=3, tags=self.label))
            self.highlighted = True

    def unhighlight(self):
        if self.highlighted:
            self.canvas.delete(self.parts.pop())
            self.highlighted = False

    def bind_to_canvas(self, canvas):
        if self.dynamic:
            canvas.tag_bind(self.label, '<Button-1>', self.on_click)
            canvas.tag_bind(self.label, '<B1-Motion>', self.on_motion)
            canvas.tag_bind(self.label, '<ButtonRelease-1>', self.on_release)
            canvas.tag_bind(self.label, '<Enter>', self.show_tooltip)
            canvas.tag_bind(self.label, '<Leave>', self.hide_tooltip)
            canvas.tag_bind(self.label, RIGHT_CLICK, self.rotate)
            canvas.tag_bind(self.label, '<Control-Button-1>', self.delete)
        self.canvas = canvas

    def on_click(self, event):
        self.total_dx = self.total_dy = 0
        self.start_x, self.start_y = event.x, event.y
        self.moving = True
        for p in self.parts:
            self.canvas.lift(p)
        self.highlight()

    def on_motion(self, event):
        xnew, ynew = event.x, event.y
        dx, dy = self.canvas.snap_to(xnew-self.start_x, ynew-self.start_y)
        if dx != 0 or dy != 0:
            # We're moving multiple components
            if len(self.canvas.selection) > 0 and self in self.canvas.selection:
                for c in self.canvas.selection:
                    c.move(dx, dy)
            else:
                self.move(dx, dy)
        self.start_x += dx
        self.start_y += dy
        self.total_dx += dx
        self.total_dy += dy

    def on_release(self, event):
        # Unhighlighting multiple components
        self.moving = False
        if len(self.canvas.selection) > 0 and self in self.canvas.selection:
            for c in self.canvas.selection:
                c.unhighlight()
            self.ui.move_components(self.total_dx, self.total_dy, *self.canvas.selection)
            self.canvas.selection = []
        else:
            self.unhighlight()
            self.ui.move_components(self.total_dx, self.total_dy, self)

    def rotate(self, event):
        pass

    def delete(self, event):
        self.ui.remove_component(self)
        self.erase()


suffix = [' ohm', '0 ohm', 'K', 'K', '0K', 'M', 'M', '0M', 'G', 'G']


def res_to_str(res=None):  # TODO: Make this a class method of resistor?
    res = [1, 0, 2] if res is None else res  # Default value of 1k
    if res[0] == 0:  # deal with small values of resistance
        value = str(res[1])
        if res[2] % 3 == 2:  # indent
            value = '0' + '.' + value[0]  # indent
    else:
        value = str(res[0]) + str(res[1])
        if res[2] % 3 == 2:  # indent
            value = value[0] + '.' + value[1]  # indent
    value += suffix[res[2]]
    return value


# Convert string to our resistance representation
# hartz, Feb 13 2011
def str_to_res(s):
    orig = s = str(s)
    s = s.lower().replace(' ', '').replace('s', '').replace(",", "")
    kilo, mega, giga = s.find('kilo'), s.find('mega'), s.find('giga')
    s = s.replace('ohm', '').replace('kilo', '').replace('mega', '').replace('giga', '')
    k, m, g = s.find('k'), s.find('m'), s.find('g')
    s = s.replace('o', '').replace('k', '').replace('m', '').replace('g', '')
    try:
        n = float(s)
    except:
        return 0
    mul = max(1, 1e3 * (kilo > -1 or k > -1)) * max(1, 1e6 * (mega > -1 or m > -1)) * max(1, 1e9 * (
    giga > -1 or g > -1))
    n = n * mul
    if 1e11 <= n:
        return 1
    elif 1 > n:
        return -1
    e = 0
    while 10 ** (e + 1) <= n:
        e = e + 1
    coeff = n / (10 ** e)
    coeff = int(coeff * 10)
    if e == 0:
        return [0, coeff // 10, 0]
    else:
        return [coeff // 10, coeff % 10, e - 1]


class Resistor(Component):
    res_dict = {'sh': {'offset': (18, 0),
                       'rects': [(-20, -2, 20, 2), (-15, -5, 15, 5), (-11, -4, -7, 4), (-3, -4, 1, 4), (5, -4, 9, 4)],
                       'rotation': (-18, 36, False, True),
                       'grid': (-18, 0, 18, 0)},
                'sv': {'offset': (0, -18),
                       'rects': [(-2, -20, 2, 20), (-5, -15, 5, 15), (-4, -11, 4, -7), (-4, -3, 4, 1), (-4, 5, 4, 9)],
                       'rotation': (0, -18, True, True),
                       'grid': (0, -18, 0, 18)},
                'lh': {'offset': (24, 0),
                       'rects': [(-26, -2, 26, 2), (-15, -5, 15, 5), (-11, -4, -7, 4), (-3, -4, 1, 4), (5, -4, 9, 4)],
                       'rotation': (-24, 48, False, False),
                       'grid': (-24, 0, 24, 0)},
                'lv': {'offset': (0, -24),
                       'rects': [(-2, -26, 2, 26), (-5, -15, 5, 15), (-4, -11, 4, -7), (-4, -3, 4, 1), (-4, 5, 4, 9)],
                       'rotation': (0, -24, True, False),
                       'grid': (0, -24, 0, 24)}}

    def __init__(self, z, c1, c2, c3, ui, horizontal=False, short=True, dynamic=True):
        Component.__init__(self, ui, dynamic)
        self.text = res_to_str((c1, c2, c3))
        self.tip = None
        if short and horizontal:
            self.type = 'sh'
        elif short and not horizontal:
            self.type = 'sv'
        elif not short and horizontal:
            self.type = 'lh'
        else:
            self.type = 'lv'
        x0, y0 = z
        self.c1, self.c2, self.c3 = c1, c2, c3
        dx, dy = self.res_dict[self.type]['offset']
        self.x, self.y = x0+dx, y0+dy
        self.label = get_label(self.type)

    def show_tooltip(self, event):
        if not self.moving:
            x = event.x + self.ui.work_canvas.winfo_rootx()+10
            y = event.y + self.ui.work_canvas.winfo_rooty()+10
            if not self.tip:
                self.tip = tw = Toplevel(self.ui.work_canvas)
                tw.wm_overrideredirect(1)
                tw.wm_geometry("+%d+%d" % (x, y))
                try:
                    # For Mac OS
                    tw.tk.call("::tk::unsupported::MacWindowStyle", "style", tw._w, "help", "noActivates")
                except TclError:
                    pass
                l = Label(tw, text=self.text, justify=LEFT, background="#ffffe0", relief=SOLID, borderwidth=1,
                          font=DEFAULT_FONT)
                l.pack()
            else:
                self.tip.geometry("+%d+%d" % (x, y))

    def hide_tooltip(self, event=None):
        if self.tip is None:
            return
        tw = self.tip
        self.tip = None
        if tw:
            tw.destroy()

    def add(self, canvas):
        x, y = self.x, self.y
        c1, c2, c3 = self.c1, self.c2, self.c3
        self.canvas = c = canvas
        rects = [(x+t[0], y+t[1], x+t[2], y+t[3]) for t in self.res_dict[self.type]['rects']]
        self.parts = [c.create_rectangle(*rects[0], fill=BLACK, outline=BLACK, tags=self.label),
                      c.create_rectangle(*rects[1], fill=BODY, outline=GRAY, tags=self.label),
                      c.create_rectangle(*rects[2], fill=COLORS[c1], outline=COLORS[c1], tags=self.label),
                      c.create_rectangle(*rects[3], fill=COLORS[c2], outline=COLORS[c2], tags=self.label),
                      c.create_rectangle(*rects[4], fill=COLORS[c3], outline=COLORS[c3], tags=self.label)]
        self.bind_to_canvas(canvas)

    def rotate(self, event=None, update=True):
        self.hide_tooltip()
        dx, dy, new_horizontal, new_short = self.res_dict[self.type]['rotation']
        self.__init__((self.x+dx, self.y+dy), self.c1, self.c2, self.c3, self.ui, horizontal=new_horizontal,
                      short=new_short)
        self.ui.rotate_component(self, update)

    def __str__(self):
        x, y = self.x, self.y
        offsets = self.res_dict[self.type]['grid']
        x0, y0, x1, y1 = ijgrid(x+offsets[0], y+offsets[1]) + ijgrid(x+offsets[2], y+offsets[3])
        return 'resistor(%d,%d,%d): (%d,%d)--(%d,%d)' % (self.c1, self.c2, self.c3, x0, y0, x1, y1)


class DisplayResistor(Resistor):
    def __init__(self, z, c1, c2, c3, ui):
        Resistor.__init__(self, z, c1, c2, c3, ui, horizontal=True, short=True, dynamic=False)

    def in1(self, x, y):
        return self.y-8 < y < self.y+8 and self.x-11 < x < self.x-7

    def in2(self, x, y):
        return self.y-8 < y < self.y+8 and self.x-3 < x < self.x+1

    def in3(self, x, y):
        return self.y-8 < y < self.y+8 and self.x+5 < x < self.x+9


class OpAmp(Component):
    def __init__(self, z, ui, inverted=False, dynamic=True):
        Component.__init__(self, ui, dynamic)
        self.inverted = inverted
        x, y = z
        if self.inverted:
            self.x, self.y = x-18, y+18
        else:
            self.x, self.y = x+18, y-18
        self.label = get_label('op')

    def add(self, canvas):
        x, y = self.x, self.y
        self.parts = [canvas.create_rectangle(x - 20, y - 19, x - 16, y + 19, fill=BLACK, outline=BLACK, tags=self.label),
                      canvas.create_rectangle(x - 8, y - 19, x - 4, y + 19, fill=BLACK, outline=BLACK, tags=self.label),
                      canvas.create_rectangle(x + 4, y - 19, x + 8, y + 19, fill=BLACK, outline=BLACK, tags=self.label),
                      canvas.create_rectangle(x + 16, y - 19, x + 20, y + 19, fill=BLACK, outline=BLACK, tags=self.label),
                      canvas.create_rectangle(x - 21, y - 16, x + 21, y + 16, fill=GRAY, outline=BLACK, tags=self.label)]
        if self.inverted:
            self.parts.append(canvas.create_oval(x + 20, y - 4, x + 10, y - 14, fill=BODY, outline=BLACK, tags=self.label))
        else:
            self.parts.append(canvas.create_oval(x - 20, y + 4, x - 10, y + 14, fill=BODY, outline=BLACK, tags=self.label))
        self.bind_to_canvas(canvas)

    def rotate(self, event=None, update=True):
        if self.inverted:
            dx, dy, new_inverted = -18, 18, False
        else:
            dx, dy, new_inverted = 18, -18, True
        self.__init__((self.x+dx, self.y+dy), self.ui, new_inverted, dynamic=True)
        self.ui.rotate_component(self, update)

    def __str__(self):
        x, y = self.x, self.y
        if self.inverted:
            x0, y0, x1, y1 = ijgrid(x+18, y-18) + ijgrid(x+18, y+18)
        else:
            x0, y0, x1, y1 = ijgrid(x-18, y+18) + ijgrid(x-18, y-18)
        return 'opamp: (%d,%d)--(%d,%d)'%(x0, y0, x1, y1)


class Pot(Component):
    def __init__(self, z, ui, inverted=False, dynamic=True):
        Component.__init__(self, ui, dynamic)
        self.inverted = inverted
        x, y = z
        if self.inverted:
            self.x, self.y = x-12, y+12
        else:
            self.x, self.y = x+12, y-12
        self.label = get_label('po')

    def add(self, canvas):
        x, y = self.x, self.y
        if self.inverted:
            self.parts = [canvas.create_rectangle(x - 20, y - 20, x + 20, y + 20, fill=GRAY, outline=BLACK, tags=self.label),
                          canvas.create_rectangle(x - 14, y - 13, x - 10, y - 9, fill=BLACK, outline=BLACK, tags=self.label),
                          canvas.create_rectangle(x - 2, y - 9, x + 2, y + 13, fill=BLACK, outline=BLACK, tags=self.label),
                          canvas.create_rectangle(x + 10, y - 13, x + 14, y - 9, fill=BLACK, outline=BLACK, tags=self.label),
                          canvas.create_oval(x - 11, y - 13, x + 11, y + 9, fill=BODY, outline=BLACK, tags=self.label),
                          canvas.create_text(x, y - 2, text='pot', font=DEFAULT_FONT, tags=self.label)]
        else:
            self.parts = [canvas.create_rectangle(x - 20, y - 20, x + 20, y + 20, fill=GRAY, outline=BLACK, tags=self.label),
                          canvas.create_rectangle(x - 14, y + 9, x - 10, y + 13, fill=BLACK, outline=BLACK, tags=self.label),
                          canvas.create_rectangle(x - 2, y - 13, x + 2, y - 9, fill=BLACK, outline=BLACK, tags=self.label),
                          canvas.create_rectangle(x + 10, y + 9, x + 14, y + 13, fill=BLACK, outline=BLACK, tags=self.label),
                          canvas.create_oval(x - 11, y - 9, x + 11, y + 13, fill=BODY, outline=BLACK, tags=self.label),
                          canvas.create_text(x, y + 2, text='pot', font=DEFAULT_FONT, tags=self.label)]
        self.bind_to_canvas(canvas)

    def rotate(self, event=None, update=True):
        if self.inverted:
            dx, dy, new_inverted = -12, 12, False
        else:
            dx, dy, new_inverted = 12, -12, True
        self.__init__((self.x+dx, self.y+dy), self.ui, new_inverted)
        self.ui.rotate_component(self, update)

    def __str__(self):
        x, y = self.x, self.y
        if self.inverted:
            x0, y0, x1, y1, x2, y2 = ijgrid(x+12, y-12) + ijgrid(x, y+12) + ijgrid(x-12, y-12)
        else:
            x0, y0, x1, y1, x2, y2 = ijgrid(x-12, y+12) + ijgrid(x, y-12) + ijgrid(x+12, y+12)
        return 'pot: (%d,%d)--(%d,%d)--(%d,%d)' % (x0, y0, x1, y1, x2, y2)


class Motor(Component):
    def __init__(self, z, ui, inverted=False, dynamic=True):
        Component.__init__(self, ui, dynamic)
        self.inverted = inverted
        self.x, self.y = z
        self.label = get_label('mo')

    def add(self, canvas):
        x, y = self.x, self.y
        if self.inverted:
            self.parts = [canvas.create_rectangle(x - 16, y - 10, x + 76, y + 80, fill=GRAY, outline=BLACK, tags=self.label),
                          canvas.create_rectangle(x - 2, y - 2, x + 2, y + 2, fill=BLACK, outline=BLACK, tags=self.label),
                          canvas.create_rectangle(x + 10, y - 2, x + 14, y + 2, fill=BLACK, outline=BLACK, tags=self.label),
                          canvas.create_rectangle(x + 22, y - 2, x + 26, y + 2, fill=BLACK, outline=BLACK, tags=self.label),
                          canvas.create_rectangle(x + 34, y - 2, x + 38, y + 2, fill=BLACK, outline=BLACK, tags=self.label),
                          canvas.create_rectangle(x + 46, y - 2, x + 50, y + 2, fill=BLACK, outline=BLACK, tags=self.label),
                          canvas.create_rectangle(x + 58, y - 2, x + 62, y + 2, fill=BLACK, outline=BLACK, tags=self.label),
                          canvas.create_rectangle(x - 6, y + 70, x + 4, y + 60, fill=BLACK, tags=self.label),
                          canvas.create_text(x + 30, y + 50, text='Motor', fill=WHITE, font=DEFAULT_FONT, tags=self.label),
                          canvas.create_text(x + 30, y + 65, text='Connector', fill=WHITE, font=DEFAULT_FONT, tags=self.label),
                          canvas.create_text(x + 60, y + 15, text='6', fill=WHITE, font=DEFAULT_FONT, tags=self.label),
                          canvas.create_text(x + 48, y + 15, text='5', fill=WHITE, font=DEFAULT_FONT, tags=self.label),
                          canvas.create_text(x + 36, y + 15, text='4', fill=WHITE, font=DEFAULT_FONT, tags=self.label),
                          canvas.create_text(x + 24, y + 15, text='3', fill=WHITE, font=DEFAULT_FONT, tags=self.label),
                          canvas.create_text(x + 12, y + 15, text='2', fill=WHITE, font=DEFAULT_FONT, tags=self.label),
                          canvas.create_text(x + 0, y + 15, text='1', fill=WHITE, font=DEFAULT_FONT, tags=self.label)]
        else:
            self.parts = [canvas.create_rectangle(x - 76, y + 10, x + 16, y - 80, fill=GRAY, outline=BLACK, tags=self.label),
                          canvas.create_rectangle(x - 62, y - 2, x - 58, y + 2, fill=BLACK, outline=BLACK, tags=self.label),
                          canvas.create_rectangle(x - 50, y - 2, x - 46, y + 2, fill=BLACK, outline=BLACK, tags=self.label),
                          canvas.create_rectangle(x - 38, y - 2, x - 34, y + 2, fill=BLACK, outline=BLACK, tags=self.label),
                          canvas.create_rectangle(x - 26, y - 2, x - 22, y + 2, fill=BLACK, outline=BLACK, tags=self.label),
                          canvas.create_rectangle(x - 14, y - 2, x - 10, y + 2, fill=BLACK, outline=BLACK, tags=self.label),
                          canvas.create_rectangle(x - 2, y - 2, x + 2, y + 2, fill=BLACK, outline=BLACK, tags=self.label),
                          canvas.create_rectangle(x - 66, y - 70, x - 56, y - 60, fill=BLACK, tags=self.label),
                          canvas.create_text(x - 30, y - 65, text='Motor', fill=WHITE, font=DEFAULT_FONT, tags=self.label),
                          canvas.create_text(x - 30, y - 50, text='Connector', fill=WHITE, font=DEFAULT_FONT, tags=self.label),
                          canvas.create_text(x, y - 15, text='1', fill=WHITE, font=DEFAULT_FONT, tags=self.label),
                          canvas.create_text(x - 12, y - 15, text='2', fill=WHITE, font=DEFAULT_FONT, tags=self.label),
                          canvas.create_text(x - 24, y - 15, text='3', fill=WHITE, font=DEFAULT_FONT, tags=self.label),
                          canvas.create_text(x - 36, y - 15, text='4', fill=WHITE, font=DEFAULT_FONT, tags=self.label),
                          canvas.create_text(x - 48, y - 15, text='5', fill=WHITE, font=DEFAULT_FONT, tags=self.label),
                          canvas.create_text(x - 60, y - 15, text='6', fill=WHITE, font=DEFAULT_FONT, tags=self.label)]
        self.bind_to_canvas(canvas)

    def rotate(self, event=None, update=True):
        if self.inverted:
            dx, dy, new_inverted = 60, 70, False
        else:
            dx, dy, new_inverted = -60, -70, True
        self.__init__((self.x+dx, self.y+dy), self.ui, new_inverted)
        self.ui.rotate_component(self, update)

    def __str__(self):
        x, y = self.x, self.y
        if self.inverted:
            x0, y0, x1, y1 = ijgrid(x, y) + ijgrid(x+60, y)
        else:
            x0, y0, x1, y1 = ijgrid(x, y) + ijgrid(x-60, y)
        t = x0, y0, x1, y1
        return 'motor: (%d,%d)--(%d,%d)' % t


class Robot(Component):
    def __init__(self, z, ui, inverted=False, dynamic=True):
        Component.__init__(self, ui, dynamic)
        self.inverted = inverted
        self.x, self.y = z
        self.label = get_label('ro')

    def add(self, canvas):
        x, y = self.x, self.y
        if self.inverted:
            self.parts = [canvas.create_rectangle(x - 16, y - 10, x + 100, y + 80, fill=GRAY, outline=BLACK, tags=self.label),
                          canvas.create_rectangle(x - 2, y - 2, x + 2, y + 2, fill=BLACK, outline=BLACK, tags=self.label),
                          canvas.create_rectangle(x + 10, y - 2, x + 14, y + 2, fill=BLACK, outline=BLACK, tags=self.label),
                          canvas.create_rectangle(x + 22, y - 2, x + 26, y + 2, fill=BLACK, outline=BLACK, tags=self.label),
                          canvas.create_rectangle(x + 34, y - 2, x + 38, y + 2, fill=BLACK, outline=BLACK, tags=self.label),
                          canvas.create_rectangle(x + 46, y - 2, x + 50, y + 2, fill=BLACK, outline=BLACK, tags=self.label),
                          canvas.create_rectangle(x + 58, y - 2, x + 62, y + 2, fill=BLACK, outline=BLACK, tags=self.label),
                          canvas.create_rectangle(x + 70, y - 2, x + 74, y + 2, fill=BLACK, outline=BLACK, tags=self.label),
                          canvas.create_rectangle(x + 82, y - 2, x + 86, y + 2, fill=BLACK, outline=BLACK, tags=self.label),
                          canvas.create_rectangle(x - 6, y + 60, x + 4, y + 70, fill=YELLOW, tags=self.label),
                          canvas.create_text(x + 42, y + 50, text='Robot', fill=WHITE, font=DEFAULT_FONT, tags=self.label),
                          canvas.create_text(x + 42, y + 65, text='Connector', fill=WHITE, font=DEFAULT_FONT, tags=self.label),
                          canvas.create_text(x + 84, y + 15, text='8', fill=WHITE, font=DEFAULT_FONT, tags=self.label),
                          canvas.create_text(x + 72, y + 15, text='7', fill=WHITE, font=DEFAULT_FONT, tags=self.label),
                          canvas.create_text(x + 60, y + 15, text='6', fill=WHITE, font=DEFAULT_FONT, tags=self.label),
                          canvas.create_text(x + 48, y + 15, text='5', fill=WHITE, font=DEFAULT_FONT, tags=self.label),
                          canvas.create_text(x + 36, y + 15, text='4', fill=WHITE, font=DEFAULT_FONT, tags=self.label),
                          canvas.create_text(x + 24, y + 15, text='3', fill=WHITE, font=DEFAULT_FONT, tags=self.label),
                          canvas.create_text(x + 12, y + 15, text='2', fill=WHITE, font=DEFAULT_FONT, tags=self.label),
                          canvas.create_text(x + 0, y + 15, text='1', fill=WHITE, font=DEFAULT_FONT, tags=self.label)]
        else:
            self.parts = [canvas.create_rectangle(x - 100, y + 10, x + 16, y - 80, fill=GRAY, outline=BLACK, tags=self.label),
                          canvas.create_rectangle(x - 86, y - 2, x - 82, y + 2, fill=BLACK, outline=BLACK, tags=self.label),
                          canvas.create_rectangle(x - 74, y - 2, x - 70, y + 2, fill=BLACK, outline=BLACK, tags=self.label),
                          canvas.create_rectangle(x - 62, y - 2, x - 58, y + 2, fill=BLACK, outline=BLACK, tags=self.label),
                          canvas.create_rectangle(x - 50, y - 2, x - 46, y + 2, fill=BLACK, outline=BLACK, tags=self.label),
                          canvas.create_rectangle(x - 38, y - 2, x - 34, y + 2, fill=BLACK, outline=BLACK, tags=self.label),
                          canvas.create_rectangle(x - 26, y - 2, x - 22, y + 2, fill=BLACK, outline=BLACK, tags=self.label),
                          canvas.create_rectangle(x - 14, y - 2, x - 10, y + 2, fill=BLACK, outline=BLACK, tags=self.label),
                          canvas.create_rectangle(x - 2, y - 2, x + 2, y + 2, fill=BLACK, outline=BLACK, tags=self.label),
                          canvas.create_rectangle(x - 90, y - 70, x - 80, y - 60, fill=YELLOW, tags=self.label),
                          canvas.create_text(x - 42, y - 65, text='Robot', fill=WHITE, font=DEFAULT_FONT, tags=self.label),
                          canvas.create_text(x - 42, y - 50, text='Connector', fill=WHITE, font=DEFAULT_FONT, tags=self.label),
                          canvas.create_text(x, y - 15, text='1', fill=WHITE, font=DEFAULT_FONT, tags=self.label),
                          canvas.create_text(x - 12, y - 15, text='2', fill=WHITE, font=DEFAULT_FONT, tags=self.label),
                          canvas.create_text(x - 24, y - 15, text='3', fill=WHITE, font=DEFAULT_FONT, tags=self.label),
                          canvas.create_text(x - 36, y - 15, text='4', fill=WHITE, font=DEFAULT_FONT, tags=self.label),
                          canvas.create_text(x - 48, y - 15, text='5', fill=WHITE, font=DEFAULT_FONT, tags=self.label),
                          canvas.create_text(x - 60, y - 15, text='6', fill=WHITE, font=DEFAULT_FONT, tags=self.label),
                          canvas.create_text(x - 72, y - 15, text='7', fill=WHITE, font=DEFAULT_FONT, tags=self.label),
                          canvas.create_text(x - 84, y - 15, text='8', fill=WHITE, font=DEFAULT_FONT, tags=self.label)]
        self.bind_to_canvas(canvas)

    def rotate(self, event=None, update=True):
        if self.inverted:
            dx, dy, new_inverted = 84, 60, False
        else:
            dx, dy, new_inverted = -84, -60, True
        self.__init__((self.x+dx, self.y+dy), self.ui, new_inverted)
        self.ui.rotate_component(self, update)

    def __str__(self):
        x, y = self.x, self.y
        if self.inverted:
            x0, y0, x1, y1 = ijgrid(x, y) + ijgrid(x+84, y)
        else:
            x0, y0, x1, y1 = ijgrid(x, y) + ijgrid(x-84, y)
        return 'robot: (%d,%d)--(%d,%d)' % (x0, y0, x1, y1)


class Head(Component):
    def __init__(self, z, ui, inverted=False, dynamic=True):
        Component.__init__(self, ui, dynamic)
        self.inverted = inverted
        self.x, self.y = z
        self.label = get_label('he')

    def add(self, canvas):
        x, y = self.x, self.y
        if self.inverted:
            self.parts = [canvas.create_rectangle(x - 16, y - 10, x + 100, y + 80, fill=GRAY, outline=BLACK, tags=self.label),
                          canvas.create_rectangle(x - 2, y - 2, x + 2, y + 2, fill=BLACK, outline=BLACK, tags=self.label),
                          canvas.create_rectangle(x + 10, y - 2, x + 14, y + 2, fill=BLACK, outline=BLACK, tags=self.label),
                          canvas.create_rectangle(x + 22, y - 2, x + 26, y + 2, fill=BLACK, outline=BLACK, tags=self.label),
                          canvas.create_rectangle(x + 34, y - 2, x + 38, y + 2, fill=BLACK, outline=BLACK, tags=self.label),
                          canvas.create_rectangle(x + 46, y - 2, x + 50, y + 2, fill=BLACK, outline=BLACK, tags=self.label),
                          canvas.create_rectangle(x + 58, y - 2, x + 62, y + 2, fill=BLACK, outline=BLACK, tags=self.label),
                          canvas.create_rectangle(x + 70, y - 2, x + 74, y + 2, fill=BLACK, outline=BLACK, tags=self.label),
                          canvas.create_rectangle(x + 82, y - 2, x + 86, y + 2, fill=BLACK, outline=BLACK, tags=self.label),
                          canvas.create_rectangle(x - 6, y + 60, x + 4, y + 70, fill=RED, tags=self.label),
                          canvas.create_text(x + 42, y + 50, text='Head', fill=WHITE, font=DEFAULT_FONT, tags=self.label),
                          canvas.create_text(x + 42, y + 65, text='Connector', fill=WHITE, font=DEFAULT_FONT, tags=self.label),
                          canvas.create_text(x + 84, y + 15, text='8', fill=WHITE, font=DEFAULT_FONT, tags=self.label),
                          canvas.create_text(x + 72, y + 15, text='7', fill=WHITE, font=DEFAULT_FONT, tags=self.label),
                          canvas.create_text(x + 60, y + 15, text='6', fill=WHITE, font=DEFAULT_FONT, tags=self.label),
                          canvas.create_text(x + 48, y + 15, text='5', fill=WHITE, font=DEFAULT_FONT, tags=self.label),
                          canvas.create_text(x + 36, y + 15, text='4', fill=WHITE, font=DEFAULT_FONT, tags=self.label),
                          canvas.create_text(x + 24, y + 15, text='3', fill=WHITE, font=DEFAULT_FONT, tags=self.label),
                          canvas.create_text(x + 12, y + 15, text='2', fill=WHITE, font=DEFAULT_FONT, tags=self.label),
                          canvas.create_text(x + 0, y + 15, text='1', fill=WHITE, font=DEFAULT_FONT, tags=self.label)]
        else:
            self.parts = [canvas.create_rectangle(x - 100, y + 10, x + 16, y - 80, fill=GRAY, outline=BLACK, tags=self.label),
                          canvas.create_rectangle(x - 86, y - 2, x - 82, y + 2, fill=BLACK, outline=BLACK, tags=self.label),
                          canvas.create_rectangle(x - 74, y - 2, x - 70, y + 2, fill=BLACK, outline=BLACK, tags=self.label),
                          canvas.create_rectangle(x - 62, y - 2, x - 58, y + 2, fill=BLACK, outline=BLACK, tags=self.label),
                          canvas.create_rectangle(x - 50, y - 2, x - 46, y + 2, fill=BLACK, outline=BLACK, tags=self.label),
                          canvas.create_rectangle(x - 38, y - 2, x - 34, y + 2, fill=BLACK, outline=BLACK, tags=self.label),
                          canvas.create_rectangle(x - 26, y - 2, x - 22, y + 2, fill=BLACK, outline=BLACK, tags=self.label),
                          canvas.create_rectangle(x - 14, y - 2, x - 10, y + 2, fill=BLACK, outline=BLACK, tags=self.label),
                          canvas.create_rectangle(x - 2, y - 2, x + 2, y + 2, fill=BLACK, outline=BLACK, tags=self.label),
                          canvas.create_rectangle(x - 90, y - 70, x - 80, y - 60, fill=RED, tags=self.label),
                          canvas.create_text(x - 42, y - 65, text='Head', fill=WHITE, font=DEFAULT_FONT, tags=self.label),
                          canvas.create_text(x - 42, y - 50, text='Connector', fill=WHITE, font=DEFAULT_FONT, tags=self.label),
                          canvas.create_text(x, y - 15, text='1', fill=WHITE, font=DEFAULT_FONT, tags=self.label),
                          canvas.create_text(x - 12, y - 15, text='2', fill=WHITE, font=DEFAULT_FONT, tags=self.label),
                          canvas.create_text(x - 24, y - 15, text='3', fill=WHITE, font=DEFAULT_FONT, tags=self.label),
                          canvas.create_text(x - 36, y - 15, text='4', fill=WHITE, font=DEFAULT_FONT, tags=self.label),
                          canvas.create_text(x - 48, y - 15, text='5', fill=WHITE, font=DEFAULT_FONT, tags=self.label),
                          canvas.create_text(x - 60, y - 15, text='6', fill=WHITE, font=DEFAULT_FONT, tags=self.label),
                          canvas.create_text(x - 72, y - 15, text='7', fill=WHITE, font=DEFAULT_FONT, tags=self.label),
                          canvas.create_text(x - 84, y - 15, text='8', fill=WHITE, font=DEFAULT_FONT, tags=self.label)]
        self.bind_to_canvas(canvas)

    def rotate(self, event=None, update=True):
        if self.inverted:
            dx, dy, new_inverted = 84, 60, False
        else:
            dx, dy, new_inverted = -84, -60, True
        self.__init__((self.x+dx, self.y+dy), self.ui, new_inverted)
        self.ui.rotate_component(self, update)

    def __str__(self):
        x, y = self.x, self.y
        if self.inverted:
            coords = ijgrid(x, y) + ijgrid(x+84, y)
        else:
            coords = ijgrid(x, y) + ijgrid(x-84, y)
        return 'head: (%d,%d)--(%d,%d)' % coords


class Power(Component):
    def __init__(self, z, ui, dynamic=True):
        Component.__init__(self, ui, dynamic)
        self.x, self.y = z
        self.label = get_label('pw')

    def add(self, canvas):
        x, y = self.x, self.y
        self.parts = [canvas.create_rectangle(x - 10, y - 5, x + 30, y + 10, fill=RED, outline=BLACK, tags=self.label),
                      canvas.create_rectangle(x - 2, y - 2, x + 2, y + 2, fill=BLACK, outline=BLACK, tags=self.label),
                      canvas.create_text(x + 17, y + 2, text='+10', fill=WHITE, font=DEFAULT_FONT, tags=self.label)]
        self.bind_to_canvas(canvas)

    def __str__(self):
        return '+10: (%d,%d)' % ijgrid(self.x, self.y)


class Ground(Component):
    def __init__(self, z, ui, dynamic=True):
        Component.__init__(self, ui, dynamic)
        self.x, self.y = z
        self.label = get_label('gd')

    def add(self, canvas):
        x, y = self.x, self.y
        self.parts = [canvas.create_rectangle(x - 10, y - 10, x + 30, y + 5, fill=BLUE, outline=BLACK, tags=self.label),
                      canvas.create_rectangle(x - 2, y - 2, x + 2, y + 2, fill=BLACK, outline=BLACK, tags=self.label),
                      canvas.create_text(x + 17, y - 2, text='gnd', fill=WHITE, font=DEFAULT_FONT, tags=self.label)]
        self.bind_to_canvas(canvas)

    def __str__(self):
        return 'gnd: (%d,%d)' % ijgrid(self.x, self.y)


class PositiveProbe(Component):
    def __init__(self, z, ui, dynamic=True):
        Component.__init__(self, ui, dynamic)
        self.x, self.y = z
        self.label = get_label('pp')

    def add(self, canvas):
        x, y = self.x, self.y
        self.parts = [canvas.create_rectangle(x - 20, y - 5, x + 20, y + 20, fill=RED, outline=BLACK, tags=self.label),
                      canvas.create_rectangle(x - 2, y - 2, x + 2, y + 2, fill=BLACK, outline=BLACK, tags=self.label),
                      canvas.create_text(x, y + 10, text='+probe', fill=WHITE, font=DEFAULT_FONT, tags=self.label)]
        self.bind_to_canvas(canvas)

    def __str__(self):
        return '+probe: (%d,%d)' % ijgrid(self.x, self.y)


class NegativeProbe(Component):
    def __init__(self, z, ui, dynamic=True):
        Component.__init__(self, ui, dynamic)
        self.x, self.y = z
        self.label = get_label('np')

    def add(self, canvas):
        x, y = self.x, self.y
        self.parts = [canvas.create_rectangle(x - 20, y - 5, x + 20, y + 20, fill=BLUE, outline=BLACK, tags=self.label),
                      canvas.create_rectangle(x - 2, y - 2, x + 2, y + 2, fill=BLACK, outline=BLACK, tags=self.label),
                      canvas.create_text(x, y + 10, text='-probe', fill=WHITE, font=DEFAULT_FONT, tags=self.label)]
        self.bind_to_canvas(canvas)

    def __str__(self):
        return '-probe: (%d,%d)' % ijgrid(self.x, self.y)


class Wire(Component):
    def __init__(self, p0, p1, ui):
        Component.__init__(self, ui, dynamic=True)
        self.x0, self.y0 = p0
        self.x1, self.y1 = p1
        self.label = get_label('wi')
        self.moving_end = None
        self.fresh = True  # When this is True, the wire is fresh and being stretched for the first time
        self.overlapped = False

    def add(self, canvas):
        self.canvas = canvas
        self.render()

    def render(self, highlighted=False):
        l = sqrt((self.x1-self.x0)**2+(self.y1-self.y0)**2)/12
        if 1 < l < 10:
            color = COLORS[int(l)]
        elif 10 <= l < 50:
            color = COLORS[int((l+9)/10)]
        else:
            color = WHITE
        self.canvas.delete(self.label)
        if highlighted:
            fill = RED
            width = 10
        else:
            fill = BLACK
            width = 8
        self.parts = [self.canvas.create_line(self.x0, self.y0, self.x1, self.y1, fill=fill, width=width,
                                              capstyle='round',tags=self.label),
                      self.canvas.create_line(self.x0, self.y0, self.x1, self.y1, fill=color, width=4, capstyle='round',
                                              tags=self.label)]
        self.find_overlaps()
        self.bind_to_canvas(self.canvas)

    def find_overlaps(self):
        other_wires = [c for c in self.ui.component_list if isinstance(c, Wire) and c is not self]
        if len(other_wires) > 0 and not (self.x0 == self.x1 and self.y0 == self.y1):
            slope_1 = self.make_slope(self.x0, self.y0, self.x1, self.y1)
            for other in other_wires:
                slope_2 = self.make_slope(other.x0, other.y0, other.x1, other.y1)
                if slope_1 is None and slope_2 is None or (slope_1 is not None and slope_2 is not None and
                                                           abs(slope_1-slope_2) < 0.3):
                    overlap = list(filter(lambda p: self.has_point(p) and other.has_point(p),
                                          [(self.x0, self.y0), (self.x1, self.y1), (other.x0, other.y0),
                                           (other.x1, other.y1)]))
                    if len(overlap) > 1:
                        self.overlapped = True
                        self.canvas.itemconfig(self.parts[0], fill=CYAN)
                        return
        self.overlapped = False
        if self.highlighted:
            self.canvas.itemconfig(self.parts[0], fill=RED, width=10)
        else:
            self.canvas.itemconfig(self.parts[0], fill=BLACK, width=8)

    def make_slope(self, x0, y0, x1, y1):
        try:
            s = (y1-y0)/(x1-x0)
        except ZeroDivisionError:
            s = None
        return s

    def has_point(self, p):
        x0, y0, x1, y1 = self.x0, self.y0, self.x1, self.y1
        if x0 == x1:
            a, b, c = 1, 0, x0
        elif y0 == y1:
            a, b, c = 0, 1, y0
        else:
            dx, dy = x1-x0, y1-y0
            a, b, c = dy, -dx, dy*x0-dx*y0
        x, y = p
        dist = abs(a*x+b*y-c)
        if dist > 36:
            return False
        min_x, min_y = min(self.x0, self.x1), min(self.y0, self.y1)
        max_x, max_y = max(self.x0, self.x1), max(self.y0, self.y1)
        if max_x == min_x:
            return abs(max_x-x) < 0.1 and min_y <= y <= max_y
        elif max_y == min_y:
            return abs(max_y-y) < 0.1 and min_x <= x <= max_x
        else:
            return min_x <= x <= max_x and min_y <= y <= max_y

    def nearend(self, x, y):
        if self.x0-7 < x < self.x0+7 and self.y0-7 < y < self.y0+7:
            return 0
        elif self.x1-7 < x < self.x1+7 and self.y1-7 < y < self.y1+7:
            return 1
        else:
            return None

    def highlight(self):
        if not self.overlapped:
            self.canvas.itemconfig(self.parts[0], fill=RED, width=10)
        self.highlighted = True

    def unhighlight(self):
        if not self.overlapped:
            self.canvas.itemconfig(self.parts[0], fill=BLACK, width=8)
        self.highlighted = False

    def on_click(self, event):
        self.total_dx = self.total_dy = 0
        self.start_x, self.start_y = event.x, event.y
        self.moving_end = self.nearend(event.x, event.y)
        if self.moving_end is not None:  # If we are stretching the wire, temporarily bind to global motion and release
            self.canvas.bind('<B1-Motion>', self.on_motion)
            self.canvas.bind('<ButtonRelease-1>', self.on_release)
        self.highlight()

    def on_motion(self, event):
        dx, dy = self.canvas.snap_to(event.x-self.start_x, event.y-self.start_y)
        if dx != 0 or dy != 0:
            if self.moving_end is None:  # Move the wire itself
                if len(self.canvas.selection) > 0 and self in self.canvas.selection:
                    for c in self.canvas.selection:
                        c.move(dx, dy)
                else:
                    self.move(dx, dy)
            elif self.moving_end == 0:  # Move x0, y0
                self.x0 += dx
                self.y0 += dy
                self.render(highlighted=True)
            elif self.moving_end == 1:  # Move x1, y1
                self.x1 += dx
                self.y1 += dy
                self.render(highlighted=True)
            self.start_x += dx
            self.start_y += dy
            self.total_dx += dx
            self.total_dy += dy

    def move(self, dx, dy):
        if dx != 0 or dy != 0:
            self.x0 += dx
            self.y0 += dy
            self.x1 += dx
            self.y1 += dy
            for p in self.parts:
                self.canvas.move(p, dx, dy)
                self.canvas.lift(p)
            self.find_overlaps()

    def on_release(self, event):
        if self.moving_end is not None:  # One of the ends has been rewired
            self.unhighlight()
            # Unbind the global methods
            self.canvas.bind('<B1-Motion>', lambda event: None)
            self.canvas.bind('<ButtonRelease-1>', lambda event: None)
            fresh = self.fresh
            if self.x0 == self.x1 and self.y0 == self.y1:  # The wire has zero length
                self.ui.remove_component(self, False)
                if self.fresh:  # Silently discard a zero-length initial wire, and return
                    return
                vanish = True
            else:
                self.fresh = False
                vanish = False
            self.ui.wire_component(self, self.moving_end, self.total_dx, self.total_dy, fresh, vanish)
        else:  # The wire itself has been moved
            if len(self.canvas.selection) > 0 and self in self.canvas.selection:
                for c in self.canvas.selection:
                    c.unhighlight()
                self.ui.move_components(self.total_dx, self.total_dy, *self.canvas.selection)
                self.canvas.selection = []
            else:
                self.unhighlight()
                self.ui.move_components(self.total_dx, self.total_dy, self)

    def __str__(self):
        coords = ijgrid(self.x0, self.y0) + ijgrid(self.x1, self.y1)
        return 'wire: (%d,%d)--(%d,%d)' % coords

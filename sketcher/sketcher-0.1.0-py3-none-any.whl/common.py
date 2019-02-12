from __future__ import division
import math
from math import sin, cos
color_tab = {
    'black': (0, 0, 0),
    'white': (255, 255, 255),
    'red': (255, 0, 0),
    'green': (0, 255, 0),
    'blue': (0, 0, 255),
    'grey': (127, 127, 127),
}


class Shape:
    def __init__(self, vertex):
        self.vertex = vertex

    def center(self):
        n = len(self.vertex)
        cx = sum(x for x, y in self.vertex)/n
        cy = sum(y for x, y in self.vertex)/n
        return cx, cy

    def rotate(self, angle, center='center'):
        newv = []
        if center == 'center':
            center = self.center()
        for x, y in self.vertex:
            dx, dy = x - center[0], y - center[1]
            dxp = dx * cos(angle) + dy * sin(angle)
            dyp = - dx * sin(angle) + dy * cos(angle)
            newv.append((center[0] + dxp, center[1] + dyp))
        return Shape(newv)

    def translate(self, vec):
        newv = []
        for i in range(len(self.vertex)):
            newv.append(self.vertex[i][0] + vec[0],
                        self.vertex[i][1] + vec[1])
        return Shape(newv)

    def copy(self):
        return Shape(self.vertex.copy())


class Color:
    def __init__(self, col):
        self.r = 0
        self.g = 0
        self.b = 0
        if isinstance(col, str):
            self.r, self.g, self.b = color_tab[col]
        elif isinstance(col, Color):
            self.r = col.r
            self.g = col.g
            self.b = col.b
        elif isinstance(col, float) or isinstance(col, int):
            if math.isnan(col):
                col = 255
            elif col < 0:
                col = 0
            elif col > 255:
                col = 255
            self.r = int(col)
            self.g = int(col)
            self.b = int(col)
        elif hasattr(col, '__iter__'):
            self.r, self.g, self.b = col
        else:
            print(type(col))
            exit()

    def hashtag(self):
        r = hex(int(self.r))[2:]
        g = hex(int(self.g))[2:]
        b = hex(int(self.b))[2:]
        if len(r) != 2:
            r = '0' + r
        if len(g) != 2:
            g = '0' + g
        if len(b) != 2:
            b = '0' + b
        return '#{}{}{}'.format(r, g, b)

    def tupple255(self):
        return (int(self.r), int(self.g), int(self.b))


class MouseState:
    def __init__(self):
        self.pos = (0, 0)
        self.pressed = set()
        self.released = set()

    def flush(self):
        self.pressed.clear()
        self.released.clear()

    def clean(self):
        still_pressed = self.pressed - self.released
        releasing = self.released.intersection(self.pressed)

        self.pressed = still_pressed
        self.released = releasing


class KeyboardState:
    def __init__(self):
        self.pressed = set()
        self.released = set()

    def flush(self):
        self.pressed.clear()
        self.released.clear()

    def clean(self):
        still_pressed = self.pressed - self.released
        releasing = self.released.intersection(self.pressed)

        self.pressed = still_pressed
        self.released = releasing

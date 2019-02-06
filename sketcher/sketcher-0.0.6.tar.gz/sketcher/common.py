import math
color_tab = {
    'black': (0, 0, 0),
    'white': (255, 255, 255),
    'red': (255, 0, 0),
    'green': (0, 255, 0),
    'blue': (0, 0, 255),
    'grey': (127, 127, 127),
}


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

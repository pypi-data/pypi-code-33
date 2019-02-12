from .common import Color


class CanvasBackend:
    def __init__(self):
        self.fill = True
        self.stroke = True
        self.back_color = Color('white')
        self.fill_color = Color('blue')
        self.stroke_color = Color('black')
        self.size = (500, 500)
        self.frame = 0.1

    def init(self):
        raise NotImplementedError

    def start(self, main_func, mod):
        raise NotImplementedError

    def clear(self):
        pass

    def set_fill(self, yes):
        self.fill = yes

    def set_frame(self, l):
        self.frame = l

    def set_stroke(self, yes):
        self.stroke = yes

    def get_mouse_state(self):
        pass

    def get_keyboard_state(self):
        pass

    def set_size(self, w, h):
        self.size = (w, h)

    def set_background(self, color):
        self.back_color = color

    def draw_shape(self, shape):
        pass

    def draw_point(self, x, y):
        pass

    def draw_line(self, x1, y1, x2, y2):
        pass

    def draw_rectangle(self, x, y, w, h):
        pass

    def draw_ellipse(self, x, y, a, b):
        pass

    def draw_text(self, x, y, text, **kwargs):
        pass

    def draw_image(self, x, y, filename, scale=(1, 1)):
        pass

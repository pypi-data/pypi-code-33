from .backend_base import CanvasBackend
from .common import KeyboardState, MouseState, Color
import pyglet as pg
from queue import Queue


def mouse_button(b):
    if b == pg.window.mouse.LEFT:
        return 1
    elif b == pg.window.mouse.RIGHT:
        return 3
    elif b == pg.window.mouse.MIDDLE:
        return 2
    else:
        return 0


def key_symbol(b):
    return pg.window.key.symbol_string(b)


class Backend(CanvasBackend):
    def __init__(self):
        CanvasBackend.__init__(self)
        self.win = pg.window.Window(vsync=0)
        self.event_queue = Queue()

        self.stroke_color = Color('black')
        self.fill_color = Color('red')
        self.back_color = Color('white')
        self.batch = pg.graphics.Batch()

        @self.win.event
        def on_key_press(symbol, modifiers):
            self.event_queue.put(('key_press', (symbol, modifiers)))

        @self.win.event
        def on_key_release(symbol, modifiers):
            self.event_queue.put(('key_release', (symbol, modifiers)))

        @self.win.event
        def on_mouse_press(x, y, button, modifiers):
            self.event_queue.put(('mouse_press', (x, y, button, modifiers)))

        @self.win.event
        def on_mouse_release(x, y, button, modifiers):
            self.event_queue.put(('mouse_release', (x, y, button, modifiers)))

        @self.win.event
        def on_mouse_motion(x, y, dx, dy):
            self.event_queue.put(('mouse_move', (x, y)))

        self.user_loop = None

        self.__keyboard_state = KeyboardState()
        self.__mouse_state = MouseState()

    def init(self):
        pass
        # setup background, canvas, focus

    def start(self, setup, loop):
        setup()
        self.user_loop = loop

        # run main loop
        self.loop()
        pg.app.run()

    def loop(self, dt=0):
        pg.clock.schedule_once(self.loop, self.frame)
        # poll event
        self.__mouse_state.clean()
        self.__keyboard_state.clean()

        while not self.event_queue.empty():
            # empty event list
            ev_type, ev = self.event_queue.get()
            if ev_type == 'key_press':
                self.__keyboard_state.pressed.add(key_symbol(ev[0]))
            elif ev_type == 'key_release':
                self.__keyboard_state.pressed.add(key_symbol(ev[0]))
            elif ev_type == 'mouse_move':
                self.__mouse_state.pos = (ev[0], self.size[1]-ev[1])

            elif ev_type == 'mouse_press':
                self.__mouse_state.pressed.add(mouse_button(ev[2]))
                self.__mouse_state.pos = (ev[0], self.size[1]-ev[1])

            elif ev_type == 'mouse_release':
                self.__mouse_state.pressed.add(mouse_button(ev[2]))
                self.__mouse_state.pos = (ev[0], self.size[1]-ev[1])

        self.__mouse_state.clean()
        self.__keyboard_state.clean()

        self.win.clear()
        self.user_loop()
        self.background.draw()
        self.batch.draw()

    def clear(self):
        # clear canvas
        self.win.clear()

    def set_fill(self, yes):
        self.fill = yes

    def set_stroke(self, yes):
        self.stroke = yes

    def set_stroke_color(self, color):
        self.stroke_color = Color(color)

    def set_fill_color(self, color):
        self.fill_color = Color(color)

    def get_mouse_state(self):
        return self.__mouse_state

    def get_keyboard_state(self):
        return self.__keyboard_state

    def set_size(self, w, h):
        self.size = (w, h)
        self.win.set_size(w, h)

    def set_background(self, color):
        self.back_color = color
        # set background color

    def draw_point(self, x, y):
        self.batch.add(1, pg.gl.GL_POINTS, None,
                       ('v2f', float(x), float(y)),
                       ('c3B', self.stroke_color.tupple255()))

    def draw_line(self, x1, y1, x2, y2):
        self.batch.add(2, pg.gl.GL_LINES, None,
                       ('v2f', (x1, y1, x2, y2)),
                       ('c3B', self.stroke_color.tupple255()*2))

    def draw_rectangle(self, x, y, w, h):
        pass

    def draw_ellipse(self, x, y, a, b):
        pass

    def draw_text(self, x, y, text, **kwargs):
        pass

    def draw_shape(self, shape):
        pass

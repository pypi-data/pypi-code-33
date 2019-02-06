from .backend_base import CanvasBackend
from .common import KeyboardState, MouseState, Color
import pyglet as pg
from queue import Queue


class Backend(CanvasBackend):
    def __init__(self):
        CanvasBackend.__init__(self)
        self.win = pg.window.Window()
        self.event_queue = Queue()

        self.stroke_color = Color('black')
        self.fill_color = Color('red')
        self.back_color = Color('white')

        def add_event(type):
            def adder(ev):
                self.event_queue.put((type, ev))
            return adder

        @self.win.event
        def on_key_press(symbol, modifiers):
            pass

        @self.win.event
        def on_key_release(symbol, modifiers):
            pass

        @self.win.event
        def on_mouse_press(x, y, button, modifiers):
            pass

        @self.win.event
        def on_mouse_release(x, y, button, modifiers):
            pass

        @self.win.event
        def on_mouse_motion(x, y, button, modifiers):
            pass

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

    def loop(self):
        #set focus, make sure next loop will run

        # poll event
        self.__mouse_state.clean()
        self.__keyboard_state.clean()

        while not self.event_queue.empty():
            # empty event list
            pass
        self.__mouse_state.clean()
        self.__keyboard_state.clean()

        self.user_loop()

    def clear(self):
        # clear canvas
        pass

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
        # set canvas size

    def set_background(self, color):
        self.back_color = color
        # set background color

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

    def draw_shape(self, shape):
        pass

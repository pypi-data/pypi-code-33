from .backend_base import CanvasBackend
from .common import KeyboardState, MouseState, Color
import tkinter as tk
from tkinter import font as tkfont
from queue import Queue


class Backend(CanvasBackend):
    def __init__(self):
        CanvasBackend.__init__(self)
        self.win = tk.Tk()
        self.can = tk.Canvas(self.win)
        self.event_queue = Queue()

        self.stroke_color = Color('black')
        self.fill_color = Color('red')
        self.back_color = Color('white')

        def add_event(type):
            def adder(ev):
                self.event_queue.put((type, ev))
            return adder

        self.can.bind('<KeyPress>', add_event('key_press'))
        self.can.bind('<KeyRelease>', add_event('key_release'))
        self.can.bind('<ButtonPress>', add_event('mouse_press'))
        self.can.bind('<ButtonRelease>', add_event('mouse_release'))
        self.can.bind('<Motion>', add_event('mouse_move'))

        self.user_loop = None

        self.__keyboard_state = KeyboardState()
        self.__mouse_state = MouseState()

        self.__pix = tk.PhotoImage(width=1, height=1)

    def init(self):
        self.can.configure(
            width=self.size[0],
            height=self.size[1],
            background=self.back_color.hashtag()
        )
        self.can.pack()
        self.win.focus_set()

    def start(self, setup, loop):
        setup()
        self.user_loop = loop
        self.win.after(int(1000*self.frame), self.loop)
        self.win.mainloop()

    def loop(self):
        self.win.after(int(1000*self.frame), self.loop)
        self.can.focus_set()

        # poll event
        self.__mouse_state.clean()
        self.__keyboard_state.clean()

        while not self.event_queue.empty():
            ev_type, ev = self.event_queue.get()
            if ev_type == 'key_press':
                if ev.keysym:
                    self.__keyboard_state.pressed.add(ev.keysym)
                else:
                    print(ev.keycode, ev.keysym)
                    raise NotImplementedError
            elif ev_type == 'key_release':
                if ev.keysym:
                    self.__keyboard_state.released.add(ev.keysym)
                else:
                    print(ev.keycode, ev.keysym)
                    raise NotImplementedError
            elif ev_type == 'mouse_move':
                self.__mouse_state.pos = (ev.x, ev.y)

            elif ev_type == 'mouse_press':
                self.__mouse_state.pressed.add(ev.num)
                self.__mouse_state.pos = (ev.x, ev.y)

            elif ev_type == 'mouse_release':
                self.__mouse_state.released.add(ev.num)
                self.__mouse_state.pos = (ev.x, ev.y)
        self.__mouse_state.clean()
        self.__keyboard_state.clean()

        self.user_loop()

    def clear(self):
        self.can.delete('all')

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
        self.can.configure(width=w, height=h)

    def set_background(self, color):
        self.back_color = color
        self.can.configure(background=color.hashtag())

    def draw_point(self, x, y):
        fill = self.stroke_color.hashtag() if self.stroke else ''
        self.__pix.put(fill)
        self.can.create_image((x, y), image=self.__pix)

    def draw_line(self, x1, y1, x2, y2):
        fill = self.stroke_color.hashtag() if self.stroke else ''
        self.can.create_line(x1, y1, x2, y2, fill=fill)

    def draw_rectangle(self, x, y, w, h):
        fill = self.fill_color.hashtag() if self.fill else ''
        outline = self.stroke_color.hashtag() if self.stroke else ''
        self.can.create_rectangle(x, y, x+w, y+h, fill=fill, outline=outline)

    def draw_ellipse(self, x, y, a, b):
        x0 = x - a/2
        x1 = x + a/2
        y0 = y - b/2
        y1 = y + b/2
        fill = self.fill_color.hashtag() if self.fill else ''
        outline = self.stroke_color.hashtag() if self.stroke else ''
        self.can.create_oval(x0, y0, x1, y1, fill=fill, outline=outline)

    def draw_text(self, x, y, text, **kwargs):
        if 'font' in kwargs:
            font = kwargs['font']
        else:
            font = tkfont.Font(self.win)
        self.can.create_text(x, y, text=text, font=font)

    def draw_shape(self, shape):
        pass

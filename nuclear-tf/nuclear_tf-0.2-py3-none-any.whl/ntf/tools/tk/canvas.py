from abc import abstractmethod, ABCMeta
from tkinter import Tk, Frame, messagebox
from .event_listener import EventListener

"""
import tkinter

from matplotlib.backends.backend_tkagg import (
    FigureCanvasTkAgg, NavigationToolbar2Tk)
# Implement the default Matplotlib key bindings.
from matplotlib.backend_bases import key_press_handler
from matplotlib.figure import Figure

import numpy as np


root = tkinter.Tk()
root.wm_title("Embedding in Tk")

fig = Figure(figsize=(5, 4), dpi=100)
t = np.arange(0, 3, .01)
fig.add_subplot(111).plot(t, 2 * np.sin(2 * np.pi * t))

canvas = FigureCanvasTkAgg(fig, master=root)  # A tk.DrawingArea.
canvas.draw()
canvas.get_tk_widget().pack(side=tkinter.TOP, fill=tkinter.BOTH, expand=1)

toolbar = NavigationToolbar2Tk(canvas, root)
toolbar.update()
canvas.get_tk_widget().pack(side=tkinter.TOP, fill=tkinter.BOTH, expand=1)
"""


class Component:
    def __init__(self, window, width, height, bg, row=0, column=0, rowspan=1, colspan=1):
        """

        :param Window window:
        """
        self.window = window
        self.listener = EventListener(self)
        self.buttons = dict()
        self.labels = dict()
        self.texts = dict()
        self.frame = Frame(self.window, relief='solid', width=width, height=height, bg=bg)
        self.frame.grid(row=row, column=column, rowspan=rowspan, colspan=colspan)

        self.set_layout()

    def set_layout(self):
        pass


class Window(metaclass=ABCMeta):
    def __init__(self):
        self.root = Tk()
        self.canvas = dict()
        self.popup = messagebox

        self.set_layout()

    # set functions

    def set_title(self, title):
        self.root.title(title)

    def set_geometry(self, w=1200, h=800, wo=100, ho=100):
        self.root.geometry('%dx%d+%d+%d' % (w, h, wo, ho))

    def set_resizable(self, h, w):
        self.root.resizable(h, w)

    # core

    def run(self):
        self.root.mainloop()

    # implement

    @abstractmethod
    def set_layout(self):
        raise NotImplementedError

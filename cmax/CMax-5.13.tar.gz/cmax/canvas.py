import sys
from tkinter import Canvas, simpledialog
from tkinter.messagebox import showwarning

from cmax.common import BOLD_FONT, grid, bus, CURSOR_NORMAL, DEFAULT_FONT, pin, RIGHT_CLICK, RED
from cmax.component import DisplayResistor, Resistor, OpAmp, Pot, Motor, Robot, Head, Power, Ground, PositiveProbe, \
    NegativeProbe, Wire, res_to_str, str_to_res, PREFIXES


class WorkCanvas(Canvas):
    def __init__(self, master=None, **kwargs):
        Canvas.__init__(self, master, **kwargs)
        self.width = kwargs['width']
        self.height = kwargs['height']
        self.selection = []
        self.scale_factor = 1.0

    # draw a connector at grid location p = (x,y)
    def draw_connector(self, p):
        (x, y) = p
        self.create_rectangle(x - 2, y - 2, x + 2, y + 2, fill='gray', outline='gray', tags='work')

    # label grid location p = (x,y) as a
    def label(self, p, a, color='black', font=DEFAULT_FONT):
        (x, y) = p
        self.create_text(x, y, text=a, font=font, fill=color, tags='work')

    # label a bus line
    def bus_line(self, y, a, color, font):
        (x0, y0) = grid(2, y)
        (x1, y1) = grid(62, y)
        self.create_line(x0, y0, x1, y1, fill=color, tags='work')
        self.label(grid(0, y), a, color, font)
        self.label(grid(64, y), a, color, font)

    # Draw the protoboard
    def draw_protoboard(self):
        # Draw the white background
        self.create_rectangle(0, 0, self.width, self.height, fill='white', outline=None, tags='work')
        # Draw all of the pins
        for i in range(1, 64):
            for j in range(1, 11):
                self.draw_connector(pin(i, j))
        for i in range(3, 62):
            if i % 6 == 2:
                continue
            for j in range(1, 5):
                self.draw_connector(bus(i, j))
        for (y, a) in zip([1, 2, 3, 4, 5, 6, 7, 8, 9, 10], ['J', 'I', 'H', 'G', 'F', 'E', 'D', 'C', 'B', 'A']):
            self.label(pin(-0.5, y), a)
            self.label(pin(64.5, y), a)
        for x in [1, 5, 10, 15, 20, 25, 30, 35, 40, 45, 60, 50, 55, 60]:
            self.label(pin(x, 0), str(x))
            self.label(pin(x, 11), str(x))
        self.bus_line(3, '+', 'red', ('Helvetica', 10, 'bold'))
        self.bus_line(0, '-', 'blue', ('Helvetica', 10, 'bold'))
        self.bus_line(21, '+', 'red', ('Helvetica', 10, 'bold'))
        self.bus_line(18, '-', 'blue', ('Helvetica', 10, 'bold'))
        self.tag_bind('work', '<Button-1>', self.on_click)
        self.tag_bind('work', '<Shift-Button-1>', self.on_shift_click)
        self.tag_bind('work', '<Shift-B1-Motion>', self.on_shift_motion)
        self.tag_bind('work', '<Shift-ButtonRelease-1>', self.on_shift_release)

    def has_point(self, x, y):  # Determine whether an x, y point is inside the canvas
        return 0 <= x <= self.width and 0 <= y <= self.height

    def on_click(self, event):
        for c in self.selection:
            c.unhighlight()
        self.selection = []
        x, y = self.snap_to(event.x, event.y)
        w = Wire((x, y), (x, y), self.master)
        self.master.add_component(w, self, False)
        w.on_click(event)

    def on_shift_click(self, event):
        self.start_x, self.start_y = event.x, event.y
        for c in self.selection:
            c.unhighlight()
        self.selection = []

    def snap_to(self, x, y):
        num = int(12*self.scale_factor)
        snap_x, snap_y = ((x+num/2)//num)*num, ((y+num/2)//num)*num
        return snap_x, snap_y

    def find_selected(self, x0, y0, x1, y1):
        # Get a (flat) set of every tag overlapping the rectangle
        tags = set([tag for tags in map(self.gettags, self.find_enclosed(x0, y0, x1, y1)) for tag in tags])
        # Create a mapping from component labels to components
        tag_to_component = {c.label: c for c in self.master.component_list}
        # Get every component
        return [tag_to_component[tag] for tag in tags if tag[:2] in PREFIXES and tag in tag_to_component]

    def on_shift_motion(self, event):
        rect = self.start_x, self.start_y, event.x, event.y
        self.delete('selection')
        self.create_rectangle(*rect, fill=None, outline=RED, width=3, tags='selection')
        fresh_selection = self.find_selected(*rect)
        for c in fresh_selection:
            if c not in self.selection:  # If we have just selected a component, we need to highlight it
                c.highlight()
        for c in self.selection:
            if c not in fresh_selection:  # If a component has stopped being selected, unhighlight it
                c.unhighlight()
        self.selection = fresh_selection

    def on_shift_release(self, event=None):
        # This method is bound both to shift-click release, and Shift release in general
        # This handles the case where the user lifts shift before the mouse button
        self.delete('selection')


xfresh=0        # x position where new instances appear TODO: Remove when nothing here uses these
yfresh=21       # y position where new instances appear


class ComponentCanvas(Canvas):
    def __init__(self, master):
        Canvas.__init__(self, master, width=70, height=70, background='#DFDFDF', highlightthickness=0)
        self.pack(side='left')
        self.create_rectangle(2, 2, 68, 68, width=3, fill='white', outline='black')
        self.bind('<Enter>', self.enter)
        self.bind('<Leave>', self.leave)
        self.bind('<Button-1>', self.on_click)
        self.bind(RIGHT_CLICK, self.on_right_click)
        self.ui = master.master  # Back-reference to the UI

    # Highlights the canvas on mouse hover
    def enter(self, event):
        self.create_rectangle(2, 2, 68, 68, width=3, outline='red', tags='highlight')

    # This removes the highlight
    def leave(self, event):
        self.delete('highlight')

    def on_click(self, event):
        pass

    def on_right_click(self, event):
        pass


class ResistorSelectCanvas(ComponentCanvas):
    def __init__(self, master):
        ComponentCanvas.__init__(self, master)
        self.bind('<Control-Button-1>', self.on_ctrl_click)
        self.create_text(36, 50, text='click color', font=BOLD_FONT)
        self.create_text(36, 62, text='to change', font=BOLD_FONT)
        self.value = [1, 0, 2]  # By default, value is 1k ohms
        self.resistor_tag = None
        self.update_resistor(self.value)

    def update_resistor(self, value):
        if self.resistor_tag is not None:
            self.delete(self.resistor_tag)
        self.value = value[:]
        self.resistor = DisplayResistor((18, 30), self.value[0], self.value[1], self.value[2], self.ui)
        self.resistor_tag = self.resistor.label
        self.resistor.add(self)
        res_str = res_to_str(self.value)
        self.create_text(35, 13, text=res_str, font=BOLD_FONT, tags=self.resistor_tag)

    def click_common(self, event, shift_down):
        do_update = False
        if self.resistor.in1(event.x, event.y):
            do_update = True
            increment = -1 if shift_down else 1
            new = (self.value[0] + increment) % 10
            self.value[0] = new if new != 0 or self.value[1] != 0 else (new + increment) % 10
        elif self.resistor.in2(event.x, event.y):
            do_update = True
            increment = -1 if shift_down else 1
            new = (self.value[1] + increment) % 10
            self.value[1] = new if new != 0 or self.value[0] != 0 else (new + increment) % 10
        elif self.resistor.in3(event.x, event.y):
            do_update = True
            if shift_down:
                self.value[2] = (self.value[2] - 1) % 10
            else:
                self.value[2] = (self.value[2] + 1) % 10

        if do_update:
            self.update_resistor(self.value)
            self.ui.update_resistor_canvases(self.value)

    def on_click(self, event):
        self.click_common(event, False)

    def on_right_click(self, event):
        self.click_common(event, True)

    def on_ctrl_click(self, event):
        requested = simpledialog.askstring("Resistor", "Enter Resistance Value:")
        new_value = str_to_res(requested)
        self.ui.ctrl_down = False
        self.ui.set_cursors(CURSOR_NORMAL)
        if new_value == 0:
            showwarning("CMax", "Invalid Resistance: %s" % requested)
            return
        elif new_value == 1:
            showwarning("CMax", "Resistance too large: %s" % requested)
            return
        elif new_value == -1:
            showwarning("CMax", "Resistance too small: %s" % requested)
            return
        self.update_resistor(new_value)
        self.ui.update_resistor_canvases(new_value)


class ShortResistorCanvas(ComponentCanvas):
    def __init__(self, master):
        ComponentCanvas.__init__(self, master)
        self.value = [1, 0, 2]  # 1k
        self.resistor_tag = None
        self.update_resistor(self.value)

    def update_resistor(self, value):
        if self.resistor_tag is not None:
            self.delete(self.resistor_tag)
        self.value = value[:]
        v = Resistor((35, 54), self.value[0], self.value[1], self.value[2], self.ui, horizontal=False, short=True,
                          dynamic=False)
        self.resistor_tag = v.label
        v.add(self)

    def on_right_click(self, event):
        self.ui.add_component(Resistor(grid(xfresh - 1, yfresh), self.value[0], self.value[1], self.value[2],
                                           self.ui, horizontal=True, short=True), self.ui.work_canvas)

    def on_click(self, event):
        self.ui.add_component(Resistor(grid(xfresh, yfresh + 2), self.value[0], self.value[1], self.value[2],
                                           self.ui, horizontal=False, short=True), self.ui.work_canvas)


class LongResistorCanvas(ComponentCanvas):
    def __init__(self, master):
        ComponentCanvas.__init__(self, master)
        self.value = [1, 0, 2]  #1k
        self.resistor_tag = None
        self.update_resistor(self.value)

    def update_resistor(self, value):
        if self.resistor_tag is not None:
            self.delete(self.resistor_tag)
        self.value = value[:]
        v = Resistor((35, 60), self.value[0], self.value[1], self.value[2], self.ui, horizontal=False, short=False,
                          dynamic=False)
        self.resistor_tag = v.label
        v.add(self)

    def on_right_click(self, event):
        self.ui.add_component(Resistor(grid(xfresh - 1, yfresh), self.value[0], self.value[1], self.value[2],
                                           self.ui, horizontal=True, short=False), self.ui.work_canvas)

    def on_click(self, event):
        self.ui.add_component(Resistor(grid(xfresh, yfresh + 2), self.value[0], self.value[1], self.value[2],
                                        self.ui, horizontal=False, short=False), self.ui.work_canvas)


class OpAmpCanvas(ComponentCanvas):
    def __init__(self, master):
        ComponentCanvas.__init__(self, master)
        OpAmp((18, 54), self.ui, inverted=False, dynamic=False).add(self)

    def on_click(self, event):
        self.ui.add_component(OpAmp(grid(xfresh - 1, yfresh + 2), self.ui, inverted=False), self.ui.work_canvas)

    def on_right_click(self, event):
        self.ui.add_component(OpAmp(grid(xfresh + 2, yfresh - 1), self.ui, inverted=True), self.ui.work_canvas)


class PotCanvas(ComponentCanvas):
    def __init__(self, master):
        ComponentCanvas.__init__(self, master)
        Pot((24, 48), self.ui, inverted=False, dynamic=False).add(self)

    def on_right_click(self, event):
        self.ui.add_component(Pot(grid(xfresh + 2, yfresh - 1), self.ui, inverted=True, dynamic=True), self.ui.work_canvas)

    def on_click(self, event):
        self.ui.add_component(Pot(grid(xfresh, yfresh + 1), self.ui, inverted=False, dynamic=True), self.ui.work_canvas)


class MotorCanvas(ComponentCanvas):
    def __init__(self, master):
        ComponentCanvas.__init__(self, master)
        self.create_text(34, 27, text='Motor', font=BOLD_FONT)
        self.create_text(34, 42, text='Connector', font=BOLD_FONT)

    def on_right_click(self, event):
        self.ui.add_component(Motor(grid(xfresh, yfresh - 5), self.ui, inverted=True), self.ui.work_canvas)

    def on_click(self, event):
        self.ui.add_component(Motor(grid(xfresh + 5, yfresh + 1), self.ui, inverted=False), self.ui.work_canvas)


class RobotCanvas(ComponentCanvas):
    def __init__(self, master):
        ComponentCanvas.__init__(self, master)
        self.create_text(34, 27, text='Robot', font=BOLD_FONT)
        self.create_text(34, 42, text='Connector', font=BOLD_FONT)

    def on_click(self, event):
        self.ui.add_component(Robot(grid(xfresh + 7, yfresh + 1), self.ui, inverted=False), self.ui.work_canvas)

    def on_right_click(self, event):
        self.ui.add_component(Robot(grid(xfresh, yfresh - 5), self.ui, inverted=True), self.ui.work_canvas)


class HeadCanvas(ComponentCanvas):
    def __init__(self, master):
        ComponentCanvas.__init__(self, master)
        self.create_text(34, 27, text='Head', font=BOLD_FONT)
        self.create_text(34, 42, text='Connector', font=BOLD_FONT)

    def on_right_click(self, event):
        self.ui.add_component(Head(grid(xfresh, yfresh - 5), self.ui, inverted=True), self.ui.work_canvas)

    def on_click(self, event):
        self.ui.add_component(Head(grid(xfresh + 7, yfresh + 1), self.ui, inverted=False), self.ui.work_canvas)


class PowerCanvas(ComponentCanvas):
    def __init__(self, master):
        ComponentCanvas.__init__(self, master)
        Power((24, 44), self.ui, dynamic=False).add(self)
        Ground((24, 25), self.ui, dynamic=False).add(self)

    def on_right_click(self, event):
        self.ui.add_component(Power(bus(61, 2), self.ui), self.ui.work_canvas)
        self.ui.add_component(Ground(bus(61, 1), self.ui), self.ui.work_canvas)

    def on_click(self, event):
        self.ui.add_component(Power(bus(61, 4), self.ui), self.ui.work_canvas)
        self.ui.add_component(Ground(bus(61, 3), self.ui), self.ui.work_canvas)


class ProbeCanvas(ComponentCanvas):
    def __init__(self, master):
        ComponentCanvas.__init__(self, master)
        PositiveProbe((35, 41), self.ui, dynamic=False).add(self)
        NegativeProbe((35, 12), self.ui, dynamic=False).add(self)

    def on_right_click(self, event):
        self.ui.add_component(PositiveProbe(bus(54, 2), self.ui), self.ui.work_canvas)
        self.ui.add_component(NegativeProbe(bus(58, 1), self.ui), self.ui.work_canvas)

    def on_click(self, event):
        self.ui.add_component(PositiveProbe(bus(54, 4), self.ui), self.ui.work_canvas)
        self.ui.add_component(NegativeProbe(bus(58, 3), self.ui), self.ui.work_canvas)

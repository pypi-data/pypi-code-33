#!/usr/bin/env python3
import traceback
import matplotlib
from tkinter import *
from tkinter.messagebox import *
try:
    from imp import reload
except ImportError:
    from importlib import reload

from cmax import __version__
from cmax import simulate  # TODO: Clean up simulate
from cmax.widgets import StatusBar, Meter, TextWindow
from cmax.canvas import WorkCanvas, ResistorSelectCanvas, ShortResistorCanvas, LongResistorCanvas, OpAmpCanvas, \
    PotCanvas, MotorCanvas, RobotCanvas, HeadCanvas, PowerCanvas, ProbeCanvas
from cmax.menu import CMaxMenu
from cmax.component import Wire
from cmax.common import *

matplotlib.use("TkAgg")

# windows-specific fix for weird working directory
# hartz 17 october 2012
if platform.system().lower() == 'windows':
    home = os.path.expanduser('~')
    docs = os.path.join(home, 'Documents')
    try:
        os.chdir(docs)
    except:
        try:
            os.chdir(home)
        except:
            pass


# larsj: Apple Modifier Key Fix  3/19/13

# Based on matplotlib's way of dealing with badly mapped modifier keys on apple keyboards
# see https://github.com/matplotlib/matplotlib/blob/master/lib/matplotlib/backends/backend_tkagg.py

# This set of keycodes are used for badly
# mapped keys on apple keyboards (i.e. no event.key_sym set)
keycode_lookup = {
    262145:  'Control_L',
    524320:  'Alt_L',
    524352:  'Alt_R',
    1048584: 'Super_L',
    1048592: 'Super_R',
    131074:  'Shift_L',
    131076:  'Shift_R',

    # These codes appear the very first time one presses the key
    131330:  'Shift_L',
    131332:  'Shift_R',
    }

def get_keysym(event):
    if event.keysym_num == 0 and sys.platform == "darwin" and event.keycode in keycode_lookup:
        return keycode_lookup[event.keycode]
    else:
        return event.keysym

#updated keyboard shortcuts to be more like real-people ones
#hartz, Feb 15 2011
def key_press(event):
    keysym = get_keysym(event)

    if keysym == "Control_L" or keysym == "Control_R":
        root.configure(cursor='pirate')
        root.ctrl_down = True
        root.set_cursors(CURSOR_CTRL)
    elif keysym == "Shift_L" or keysym == "Shift_R":
        root.shift_down = True
        root.set_cursors(CURSOR_SHIFT)

    if root.ctrl_down:
        key = keysym.lower()
        if key == 'q':  root.quit()
        elif key == 's' and root.shift_down: root.menu.save_as()
        elif key == 's': root.menu.save()
        elif key == 'i'and root.shift_down: root.menu.choose_sim_file()
        elif key == 'i': Simulate()
        elif key == 'o': root.menu.open_file()
        elif key == 'n': root.menu.clear()
        elif key == 'r': root.menu.revert()
        elif key == 'z': action_queue.undo()
        elif key == 'y': action_queue.redo()
        elif key == 'a': root.menu.about()
        elif key == 'd': root.menu.show_docs()
        elif key == 'w': simulate.close_all_windows()

def key_release(event):
    keysym = get_keysym(event)
    if keysym == "Control_L" or keysym == "Control_R":
        root.ctrl_down = False
    elif keysym == "Shift_L" or keysym == "Shift_R":
        root.shift_down = False
        # Needed in case the user lifts the shift key before the mouse
        root.work_canvas.on_shift_release()
    
    if root.ctrl_down:
        root.set_cursors(CURSOR_CTRL)
    elif root.shift_down:
        root.set_cursors(CURSOR_SHIFT)
    else:
        root.set_cursors(CURSOR_NORMAL)

def Simulate():
    reload(simulate)
    root.pre_modal()
    simulate.set_output()
    lines = [str(c) for c in root.component_list]
    if len(root.component_list) == 0:
        showwarning('Simulator - CMax','Error in simulation: circuit must be defined first')
        return
    try:
        if root.menu.simfilename:
            globals = {'potAlphaSignal':None,'lampAngleSignal':None,'lampDistanceSignal':None,'nSamples':100,'deltaT':0.02}
            f = open(root.menu.simfilename)
            f.close()
            exec(compile(open(root.menu.simfilename).read(), root.menu.simfilename, 'exec'),globals)
            potAlphaSignal = globals['potAlphaSignal']
            lampAngleSignal = globals['lampAngleSignal']
            lampDistanceSignal = globals['lampDistanceSignal']
            nSamples = globals['nSamples']
            deltaT = globals['deltaT']
            simulate.solve(lines,potAlphaSignal,lampAngleSignal,lampDistanceSignal,nSamples,deltaT)
        else:
            simulate.solve(lines)
        w = TextWindow(root,"Simulator - CMax","Simulation Results:",simulate.sim_output)
        simulate.add_window(w)
    except TclError as inst:
        print('TCL ERROR')
        print(traceback.format_exc())
        w = TextWindow(root,"Simulator - CMax","There was an error in simulation:","CMax encountered a graphics error.  Please save your work, restart CMax, and try again.\n\n"+simulate.sim_output)
        simulate.add_window(w)
    except Exception as inst:
        print('Error in simulation:')
        print(traceback.format_exc())
        w = TextWindow(root,"Simulator - CMax","There was an error in simulation:","An error occurred during simulation.\n\n"+simulate.sim_output+'\n\n'+traceback.format_exc())
        simulate.add_window(w)


class ActionQueue:
    def __init__(self):
        self.queue = []
        self.pointer = -1

    def clear(self):
        self.queue = []
        self.pointer = -1

    def new_action(self, name, data):
        root.set_changed(True)
        if -1*self.pointer > len(self.queue):
            self.queue = []
        elif self.pointer < -1:
            self.queue = self.queue[:self.pointer+1]
        self.pointer = -1
        self.queue.append((name, data))

    def undo(self):
        if -1*self.pointer <= len(self.queue):
            action, data = self.queue[self.pointer]
            if action == 'add':
                root.remove_component(data, update=False)
            elif action == 'remove':
                root.add_component(data, root.work_canvas, update=False)
            elif action == 'rotate':
                c = data
                c.rotate(update=False)
            elif action == 'moves':
                components, dx, dy = data
                for (c, offscreen) in components:
                    if offscreen:  # If the component was moved offscreen, re-add it
                        root.add_component(c, root.work_canvas, update=False)
                    c.move(-dx, -dy)
            elif action == 'wire':
                c, end, dx, dy, fresh, vanish = data
                if fresh:
                    root.remove_component(c, update=False)
                else:
                    if end == 0:
                        c.x0 -= dx
                        c.y0 -= dy
                    else:
                        c.x1 -= dx
                        c.y1 -= dy
                    if vanish:
                        root.add_component(c, root.work_canvas, update=False)
                        c.render()
                    else:
                        c.render()
            self.pointer -= 1
            root.set_changed(True)

    def redo(self):
        if self.pointer < -1:
            self.pointer += 1
            action, data = self.queue[self.pointer]
            if action == 'add':
                root.add_component(data, root.work_canvas, update=False)
            elif action == 'remove':
                root.remove_component(data, update=False)
            elif action == 'rotate':
                c = data
                c.rotate(update=False)
            elif action == 'moves':
                components, dx, dy = data
                for c, offscreen in components:
                    c.move(dx, dy)
                    if offscreen:  # If the component was moved offscreen, delete it silently
                        root.remove_component(c, update=False)
            elif action == 'wire':
                c, end, dx, dy, fresh, vanish = data
                if fresh:
                    root.add_component(c, root.work_canvas, update=False)
                else:
                    if end == 0:
                        c.x0 += dx
                        c.y0 += dy
                    else:
                        c.x1 += dx
                        c.y1 += dy
                    if vanish:
                        root.remove_component(c, update=False)
                    else:
                        c.render()
            root.set_changed(True)
        

class CmaxUI(Tk):
    def __init__(self):
        Tk.__init__(self)
        self.title('CMax ' + __version__)  # set initial window title
        self.configure(cursor='arrow')
        self.resizable(width=False, height=False)
        self.width = self.winfo_width()
        self.height = self.winfo_height()
        self.protocol('WM_DELETE_WINDOW', self.quit)
        self.ctrl_down = False
        self.shift_down = False
        self.changed = False
        self.component_list = []
        self.menu = CMaxMenu(self, action_queue, Simulate)
        self.config(menu=self.menu)
        self.build_canvases()
        self.status = StatusBar(self)
        self.status.update(self.menu.simfilename)
        self.status.pack(side='bottom', fill=X)
        self.meter = Meter(self)
        self.meter.set(0.0, "")
        self.meter.pack(side='bottom', fill=X)

    def set_changed(self, change):
        if self.changed and change:  # ignore if already changed
            return
        self.changed = change
        if filenameonly(self.menu.filename) == '':
            title = 'CMax ' + __version__
        else:
            title = "CMax " + __version__ + ":  %s" % filenameonly(self.menu.filename)
        if self.changed:
            root.title(title + ' (*)')  # indicate needs saving
        else:
            root.title(title)  # just file name in window title

    def update_resistor_canvases(self, value):
        self.short_res_canvas.update_resistor(value)
        self.long_res_canvas.update_resistor(value)

    def build_canvases(self):
        component_frame = Frame(self, width=830, height=90)
        component_frame.pack()
        self.res_select_canvas = ResistorSelectCanvas(component_frame)  # For selecting resistor values
        self.short_res_canvas = ShortResistorCanvas(component_frame)  # Short resistor
        self.long_res_canvas = LongResistorCanvas(component_frame)  # Long resistor
        self.opamp_canvas = OpAmpCanvas(component_frame)  # Op-amp
        self.pot_canvas = PotCanvas(component_frame)  # Potentiometer
        self.motor_canvas = MotorCanvas(component_frame)  # Motor connector
        self.robot_canvas = RobotCanvas(component_frame)  # Robot connector
        self.head_canvas = HeadCanvas(component_frame)  # Head connector
        self.power_canvas = PowerCanvas(component_frame)  # Power and ground nodes
        self.probe_canvas = ProbeCanvas(component_frame)  # Probe
        # Build the work canvas and draw the protoboard
        self.work_canvas = WorkCanvas(self, width=830, height=320, background='#FFFFFF')
        self.work_canvas.pack()
        self.work_canvas.draw_protoboard()
        # Canvas list, used later to set cursors
        self.canvas_list = [self.res_select_canvas, self.short_res_canvas, self.opamp_canvas, self.pot_canvas,
                            self.motor_canvas, self.robot_canvas, self.head_canvas, self.power_canvas,
                            self.probe_canvas, self.work_canvas, self.long_res_canvas]

    def set_cursors(self, cursor_type):
        # Clear all previous cursors
        for canvas in self.canvas_list:  # All of the canvases have a normal arrow if nothing is held down
            canvas.configure(cursor="arrow")

        if cursor_type == CURSOR_SHIFT:
            self.work_canvas.configure(cursor='cross')

        # Delete/edit for control
        if cursor_type == CURSOR_CTRL:
            for canvas in [self.res_select_canvas]:  # resistor value entry
                canvas.configure(cursor="pencil")
            self.work_canvas.configure(cursor="pirate")

    # clear ctrl_down and shift_down before popping up a dialog
    # mostly needed because of new ctrl-whatev keyboard shortcuts
    # hartz, Feb 16 2011
    def pre_modal(self):
        self.ctrl_down = False
        self.shift_down = False
        self.set_cursors(CURSOR_NORMAL)

    def quit(self):
        self.pre_modal()
        if len(self.component_list) != 0 and root.changed:
            if str(askquestion("Save File - CMax", "Current circuit not saved -- save?")) == 'yes':
                self.menu.save()
        Tk.quit(self)

    def is_duplicate(self, c):
        if isinstance(c, Wire):  # Don't try to test for duplicate wires; overlap is handled elsewhere
            return False
        for other in self.component_list:
            if c.__class__.__name__ == other.__class__.__name__ and c.x == other.x and c.y == other.y:
                return True
        return False

    def add_component(self, c, canvas, update=True):
        c.add(canvas)
        if not isinstance(c, Wire):
            while self.is_duplicate(c):
                if not self.work_canvas.has_point(c.x, c.y):  # If this happens, we've run out of room, so erase it
                    self.remove_component(c, update=False)
                    break
                c.move(GRID_WIDTH, 0)
        self.component_list.append(c)
        if update:
            action_queue.new_action('add', c)

    def remove_component(self, c, update=True):
        c.erase()
        try:
            self.component_list.remove(c)
        except ValueError:  # Probably already removed
            pass
        if update:
            action_queue.new_action('remove', c)

    def rotate_component(self, c, update=True):
        self.remove_component(c, update=False)
        self.add_component(c, self.work_canvas, update=False)
        if update:
            action_queue.new_action('rotate', c)

    def move_components(self, dx, dy, *components):
        l = []
        for c in components:
            x0, y0, x1, y1 = self.work_canvas.bbox(c.label)  # Find the bounding box
            # Set the offscreen flag based on whether the move took the component offscreen
            offscreen = not self.work_canvas.has_point(x0, y0) and not self.work_canvas.has_point(x1, y1)
            if offscreen:  # If it did, remove it from the list without creating an action
                self.remove_component(c, update=False)
            l.append((c, offscreen))
        action_queue.new_action('moves', (l, dx, dy))

    def wire_component(self, c, end, dx, dy, fresh, vanish):
        action_queue.new_action('wire', (c, end, dx, dy, fresh, vanish))

    def reset(self):
        while self.component_list:
            self.remove_component(root.component_list[0], update=False)
        action_queue.clear()


# main routine
def main():
    global action_queue, root, menu
    action_queue = ActionQueue()
    root = CmaxUI()
    menu = root.menu
    root.bind('<KeyPress>', key_press)
    root.bind('<KeyRelease>', key_release)
    try:
        root.tk.call('wm', 'iconphoto', root._w, PhotoImage(data=ICON_IMGDATA))
    except:
        pass
    if len(sys.argv)>1:
        root.menu.filename = os.path.abspath(sys.argv[1])
        root.menu.read_file(root.menu.filename)
        root.status.update(root.menu.simfilename)
    root.mainloop()

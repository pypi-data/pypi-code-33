import os
import re
import webbrowser
from tkinter import Menu, filedialog
from tkinter.messagebox import askquestion, showwarning

from cmax.common import grid, CMAX_DOCS_URL, filenameonly, directoryonly
from cmax.component import Resistor, OpAmp, Pot, Motor, Robot, Head, Power, Ground, PositiveProbe, NegativeProbe, Wire
from cmax.widgets import AboutWindow
from cmax import simulate


class CMaxMenu(Menu):
    def __init__(self, master, action_queue, Simulate):
        Menu.__init__(self, master, tearoff=0)
        self.action_queue = action_queue
        self.filemenu = Menu(self, tearoff=0)
        self.filemenu.add_command(label="New", command=self.clear, accelerator="Ctrl+N")
        self.filemenu.add_command(label="Open...", command=self.open_file, accelerator="Ctrl+O")
        self.filemenu.add_separator()
        self.filemenu.add_command(label="Save", command=self.save, accelerator="Ctrl+S")
        self.filemenu.add_command(label="Save As...", command=self.save_as, accelerator="Ctrl+Shift+S")
        self.filemenu.add_command(label="Reload From Disk", command=self.revert, accelerator="Ctrl+R")
        self.filemenu.add_separator()
        self.filemenu.add_command(label="Quit", command=self.master.quit, accelerator="Ctrl+Q")
        self.add_cascade(label="File", menu=self.filemenu)
        self.editmenu = Menu(self, tearoff=0)
        self.editmenu.add_command(label="Undo", command=action_queue.undo, accelerator="Ctrl+Z")
        self.editmenu.add_command(label="Redo", command=action_queue.redo, accelerator="Ctrl+Y")
        self.add_cascade(label="Edit", menu=self.editmenu)
        self.simmenu = Menu(self, tearoff=0)
        self.simmenu.add_command(label="Load Sim File...", command=self.choose_sim_file, accelerator="Ctrl+Shift+I")
        self.simmenu.add_command(label="Run Simulation", command=Simulate, accelerator="Ctrl+I")
        self.simmenu.add_separator()
        self.simmenu.add_command(label="Close Sim Windows", command=simulate.close_all_windows(), accelerator="Crtl+W")
        self.add_cascade(label="Sim", menu=self.simmenu)
        self.helpmenu = Menu(self, tearoff=0)
        self.helpmenu.add_command(label="Documentation", command=self.show_docs, accelerator="Ctrl+D")
        self.helpmenu.add_command(label="About", command=self.about, accelerator="Ctrl+A")
        self.add_cascade(label="Help", menu=self.helpmenu)
        self.filename = os.getcwd()
        self.simfilename = os.path.join(os.path.dirname(__file__), 'sims/noInput.csim')
        #os.path.join(__file__[:__file__.find('CMaxMain.py')], 'sigFiles', 'noInput.csim')

    def save_file(self, new_filename):
        file = open(new_filename, 'w')
        print('#CMax circuit', file=file)
        for c in self.master.component_list:
            print(c, file=file)
        file.close()
        self.filename = new_filename
        self.master.set_changed(False)
        self.master.status.update(self.simfilename)

    def save_as(self):
        self.master.pre_modal()
        x = filedialog.asksaveasfilename(title="Save File As ... - CMax",
                                         filetypes=[('CMax files', '.cmax'), ('All files', '.*')],
                                         initialfile=filenameonly(self.filename),
                                         initialdir=directoryonly(self.filename))
        if x:
            self.save_file(x)

    def save(self):
        self.master.pre_modal()
        if filenameonly(self.filename) == '':
            self.save_as()
        else:
            self.save_file(self.filename)

    # Clears the canvas
    def clear(self):
        self.master.pre_modal()
        saveit = False
        if len(self.master.component_list) != 0 and self.master.changed:
            saveit = str(askquestion("New File - CMax", "Current circuit not saved -- save?")) == 'yes'
            if saveit:
                self.save()
        if (not self.master.changed) or (not saveit):
            while self.master.component_list:
                self.master.remove_component(self.master.component_list[0], update=False)
            self.filename = os.getcwd() + '/'
            self.master.set_changed(False)
            self.master.status.update(self.simfilename)
            self.action_queue.clear()

    # Reloads the circuit from disk
    def revert(self):
        self.master.pre_modal()
        saveit = False
        if len(self.master.component_list) != 0 and self.master.changed:  # If the circuit is not on disk
            if str(askquestion("New File - CMax", "Current circuit not saved -- save?")) == 'yes':
                self.save_as()

        self.master.reset()  # Reset the component list and action queue
        if self.filename != '':
            self.read_file(self.filename)

    # Read a file, adding its components to the component list and clearing the action queue
    def read_file(self, filename):  # TODO: Make this better somehow
        valid = False
        root = self.master
        for line in open(filename):
            if line.strip() == '#CMax circuit':
                valid = True
                continue
            match = re.match(r'opamp: \((\d+),(\d+)\)--\((\d+),(\d+)\)', line)
            if match:
                x0, y0, x1, y1 = match.groups()
                if int(y1) < int(y0):
                    root.add_component(OpAmp(grid(int(x0), int(y0)), root), root.work_canvas, False)
                else:
                    root.add_component(OpAmp(grid(int(x0), int(y0)), root, inverted=True), root.work_canvas, False)
            match = re.match(r'pot: \((\d+),(\d+)\)--\((\d+),(\d+)\)--\((\d+),(\d+)\)', line)
            if match:
                x0, y0, x1, y1, x2, y2 = match.groups()
                if int(y1) < int(y0):
                    root.add_component(Pot(grid(int(x0), int(y0)), root), root.work_canvas, False)
                else:
                    root.add_component(Pot(grid(int(x0), int(y0)), root, inverted=True), root.work_canvas, False)
            match = re.match(r'motor: \((\d+),(\d+)\)--\((\d+),(\d+)\)', line)
            if match:
                x0, y0, x1, y1 = match.groups()
                if int(x1) < int(x0):
                    root.add_component(Motor(grid(int(x0), int(y0)), root), root.work_canvas, False)
                else:
                    root.add_component(Motor(grid(int(x0), int(y0)), root, inverted=True), root.work_canvas, False)
            match = re.match(r'robot: \((\d+),(\d+)\)--\((\d+),(\d+)\)', line)
            if match:
                x0, y0, x1, y1 = match.groups()
                if int(x1) < int(x0):
                    root.add_component(Robot(grid(int(x0), int(y0)), root), root.work_canvas, False)
                else:
                    root.add_component(Robot(grid(int(x0), int(y0)), root, inverted=True), root.work_canvas, False)
            match = re.match(r'head: \((\d+),(\d+)\)--\((\d+),(\d+)\)', line)
            if match:
                x0, y0, x1, y1 = match.groups()
                if int(x1) < int(x0):
                    root.add_component(Head(grid(int(x0), int(y0)), root), root.work_canvas, False)
                else:
                    root.add_component(Head(grid(int(x0), int(y0)), root, inverted=True), root.work_canvas, False)
            match = re.match(r'resistor\((\d),(\d),(\d)\): \((\d+),(\d+)\)--\((\d+),(\d+)\)', line)
            if match:
                c1, c2, c3, x0, y0, x1, y1 = match.groups()
                if int(x0) == int(x1):
                    if int(y1) == int(y0) + 3:
                        root.add_component(Resistor(grid(int(x0), int(y1)), int(c1), int(c2), int(c3), root,
                                                    horizontal=False, short=True), root.work_canvas, False)
                    if int(y1) == int(y0) + 4:
                        root.add_component(Resistor(grid(int(x0), int(y1)), int(c1), int(c2), int(c3), root,
                                                    horizontal=False, short=False), root.work_canvas, False)
                if int(y0) == int(y1):
                    if int(x1) == int(x0) + 3:
                        root.add_component(Resistor(grid(int(x0), int(y1)), int(c1), int(c2), int(c3), root,
                                                    horizontal=True, short=True), root.work_canvas, False)
                    if int(x1) == int(x0) + 4:
                        root.add_component(Resistor(grid(int(x0), int(y1)), int(c1), int(c2), int(c3), root,
                                                    horizontal=True, short=False), root.work_canvas, False)
            match = re.match(r'\+10: \((\d+),(\d+)\)', line)
            if match:
                x0, y0 = match.groups()
                root.add_component(Power(grid(int(x0), int(y0)), root), root.work_canvas, False)
            match = re.match(r'gnd: \((\d+),(\d+)\)', line)
            if match:
                x0, y0 = match.groups()
                root.add_component(Ground(grid(int(x0), int(y0)), root), root.work_canvas, False)
            match = re.match(r'\+probe: \((\d+),(\d+)\)', line)
            if match:
                x0, y0 = match.groups()
                root.add_component(PositiveProbe(grid(int(x0), int(y0)), root), root.work_canvas, False)
            match = re.match(r'\-probe: \((\d+),(\d+)\)', line)
            if match:
                x0, y0 = match.groups()
                root.add_component(NegativeProbe(grid(int(x0), int(y0)), root), root.work_canvas, False)
            match = re.match(r'wire: \((\d+),(\d+)\)--\((\d+),(\d+)\)', line)
            if match:
                x0, y0, x1, y1 = match.groups()
                root.add_component(Wire(grid(int(x0), int(y0)), grid(int(x1), int(y1)), root), root.work_canvas, False)
        if len(root.component_list) == 0 or not valid:
            showwarning('Open File - CMax', 'Error reading file: this is not a valid circuit file')
            return
        root.set_changed(False)
        self.action_queue.clear()

    # Open a file, and read it
    def open_file(self):
        root = self.master
        root.pre_modal()
        saveit = False
        if len(root.component_list) != 0 and root.changed:
            saveit = str(askquestion("Save File - CMax", "Current circuit not saved -- save?")) == 'yes'
            if saveit:
                self.save()
        if (not root.changed) or (not saveit):
            x = filedialog.askopenfilename(title="Open File - CMax",
                                           defaultextension='.cmax',
                                           filetypes=[('All files', '*'), ('CMax files', '.cmax')],
                                           initialfile=filenameonly(self.filename),
                                           initialdir=directoryonly(self.filename))
            if x:
                try:
                    f = open(x)
                    if f.readline().strip() != '#CMax circuit':
                        showwarning('Open File - CMax', 'Error: specified file is not a valid CMax file')
                        return
                    f.close()
                except:
                    showwarning('Open File - CMax', 'Error: unable to open specified file')
                    return
                root.status.update(self.simfilename)
                self.filename = x
                root.reset()  # Clear the component list and action queue
                self.read_file(self.filename)

    # Choose and read a sim file
    def choose_sim_file(self):
        self.master.pre_modal()
        x = filedialog.askopenfilename(filetypes=[('Simulation files', '.csim')],
                                       initialfile=filenameonly(self.simfilename),
                                       initialdir=directoryonly(self.simfilename))
        if x:
            try:
                f = open(x)
                if f.readline().strip() != '#CMax simulation':
                    showwarning('Open Sim File - CMax', 'Error: specified file is not a valid CMax simulation file')
                    return
                f.close()
            except:
                showwarning('Open Sim File - CMax', 'Error: unable to open specified file')
                return
            self.simfilename = x
            self.master.status.update(self.simfilename)

    # open a web browser with the documentation
    # hartz, Feb 15 2011
    def show_docs(self):
        self.master.pre_modal()
        webbrowser.open(CMAX_DOCS_URL)

    def about(self):
        self.master.pre_modal()
        AboutWindow(self.master, "About CMax")

from tkinter import *
from tkinter.simpledialog import Dialog

from cmax import __version__
from cmax.common import LOGO_IMGDATA, ICON_IMGDATA, filenameonly


# simple status bar - displays loaded sim file
# hartz, Feb 15 2011
class StatusBar(Frame):
    def __init__(self, master):
        Frame.__init__(self, master)
        self.label = Label(self, bd=1, relief=SUNKEN, anchor=W)
        self.label.pack(fill=X)

    def update(self, sim_file):
        self.label.config(text="Simulation File Loaded: %s" % (filenameonly(sim_file) if sim_file != '' else 'noInput.csim'))
        self.label.update_idletasks()

# progress bar widget
# (ganked from Michael Lange <klappnase (at) freakmail (dot) de>)
# hartz, 14 March 2011
class Meter(Frame):
    def __init__(self, master, width=300, height=20, bg='lightgrey', fillcolor='limegreen',\
                 value=0.0, text=None, font=None, textcolor='black', *args, **kw):
        Frame.__init__(self, master, bg=bg, width=width, height=height, bd=1, relief=SUNKEN, *args, **kw)
        self._value = value

        self._canv = Canvas(self, bg=self['bg'], width=self['width'], height=self['height'],\
                                    highlightthickness=0, relief='flat', bd=0)
        self._canv.pack(fill='both', expand=1)
        self._rect = self._canv.create_rectangle(0, 0, 0, self._canv.winfo_reqheight(), fill=fillcolor,\
                                                 width=0)
        self._text = self._canv.create_text(self._canv.winfo_reqwidth()/2, self._canv.winfo_reqheight()/2,\
                                            text='', fill=textcolor)
        if font:
            self._canv.itemconfigure(self._text, font=font)

        self.set(value, text)
        self.bind('<Configure>', self._update_coords)

    def _update_coords(self, event):
        '''Updates the position of the text and rectangle inside the canvas when the size of
        the widget gets changed.'''
        # looks like we have to call update_idletasks() twice to make sure
        # to get the results we expect
        self._canv.update_idletasks()
        self._canv.coords(self._text, self._canv.winfo_width()/2, self._canv.winfo_height()/2)
        self._canv.coords(self._rect, 0, 0, self._canv.winfo_width()*self._value, self._canv.winfo_height())
        self._canv.update_idletasks()

    def get(self):
        return self._value, self._canv.itemcget(self._text, 'text')

    def set(self, value=0.0, text=""):
        #make the value failsafe:
        self._value = value if 0.0 < value < 1.0 else 0.0
        text = text if 0.0<value<1.0 else ""
        #if text == None:
        #    #if no text is specified use the default percentage string:
        #    text = str(int(round(100 * value))) + ' %'
        self._canv.coords(self._rect, 0, 0, self._canv.winfo_width()*value, self._canv.winfo_height())
        self._canv.itemconfigure(self._text, text=text)
        self._canv.update_idletasks()


#"About" window...do we really need this?
#makes me feel good about myself, at least
#hartz, Feb 18 2011
class AboutWindow(Dialog):
    def body(self,frm):
        logo = PhotoImage(data=LOGO_IMGDATA)#(file="cmax_logo.gif")
        logo_s = Label(frm,image=logo)
        logo_s.photo=logo
        name = Label(frm,text="Circuits Maximus",font="bold")
        version = Label(frm,text="version %s" % __version__)
        coders = Label(frm,text="(c) 2009-2014, 6.01 Staff")
        url = Label(frm,text="http://mit.edu/6.01")
        logo_s.pack()
        name.pack()
        version.pack()
        coders.pack()
        url.pack()
        self.resizable(False, False)
        try:
            self.tk.call('wm', 'iconphoto', self._w, PhotoImage(data=ICON_IMGDATA))
        except:
            pass
        #if os.name == 'nt':
        #    self.iconbitmap('cmax.ico')

    def buttonbox(self):
        pass


class TextWindow(Toplevel):  # tkSimpleDialog.Dialog):
    def __init__(self, parent, title=None, lbl="", text=""):
        Toplevel.__init__(self, parent)
        self.parent = parent
        if title:
            self.title(title)
        self.text = text
        self.label = lbl
        # tkSimpleDialog.Dialog.__init__(self,parent,title)
        self.fr = Frame(self)
        self.body(self.fr)
        self.fr.pack()
        self.buttonbox()
        # self.wait_visibility() # window needs to be visible for the grab
        # self.grab_set()

    def ok(self, rwr=None):
        # self.parent.grab_set()
        self.destroy()

    def body(self, frm):
        l = Label(frm, text=self.label)
        l.pack()
        e = Text(frm, width=75, height=20)
        e.insert(END, self.text)
        scrollbar = Scrollbar(frm)
        e.pack(side=LEFT)
        scrollbar.pack(side=RIGHT, fill=Y)
        e.config(yscrollcommand=scrollbar.set)
        scrollbar.config(command=e.yview)
        self.resizable(width=FALSE, height=FALSE)
        try:
            self.tk.call('wm', 'iconphoto', self._w, PhotoImage(ICON_IMGDATA))
        except:
            pass
        # e.focus_set()
        e['state'] = DISABLED
        # if os.name == 'nt':
        #    self.iconbitmap('cmax.ico')

    def buttonbox(self):
        box = Frame(self)
        w = Button(box, text="OK", width=10, command=self.ok, default=ACTIVE)
        w.pack(side=LEFT, padx=5, pady=5)
        self.bind("<Return>", self.ok)
        box.pack()
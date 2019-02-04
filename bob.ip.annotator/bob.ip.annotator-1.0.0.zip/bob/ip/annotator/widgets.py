#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''Widgets for easing the annotation of objects in the image'''

import tkinter
import tkinter.ttk

import warnings
import logging
logger = logging.getLogger(__name__)

import numpy
import scipy.spatial.distance
from PIL import Image, ImageTk

import bob.io.base
import bob.io.image
import bob.io.image.utils

COLOR_ACTIVE = "red"
COLOR_INACTIVE = "OliveDrab1"
COLOR_DESELECTED = "seashell2"
SHIFT = 0x0001


def zoom_point(zoom, p):
  """Helper to return a zoom-compensated values

  The point ``p`` may represent a single point or a tuple of values.
  """

  return tuple([int(round(k*zoom)) for k in p])


def unzoom_point(zoom, p):
  """Helper to return a zoom-decompensated values

  The point ``p`` may represent a single point or a tuple of values.
  """

  return tuple([int(round(k/zoom)) for k in p])


def zoom_points(zoom, points):
  """Helper that returns zoom-compensated sets of points

  Points should be a list of coordinates, typically, each in ``(y,x)``
  format, but not necessarily.  The procedure is agnostic to this.
  """

  return [zoom_point(zoom, p) for p in points]


def unzoom_points(zoom, points):
  """Helper that returns zoom-decompensated sets of points

  Points should be a list of coordinates, typically, each in ``(y,x)``
  format, but not necessarily.  The procedure is agnostic to this.
  """

  return [unzoom_point(zoom, p) for p in points]



class Annotation(object):
  """An annotation is a collection of points where the user clicked

  The points are assumed to be scaled-down or up according to the zoom of the
  displayed image.  It is the job of the caller to apply the correct conversion
  ratios necessary for this operation.

  An annotation can be drawn, made active and inactive on the screen.  When
  active, the annotation is editable with keyboard shortcuts.


  Parameters:

    canvas (:py:obj:`object`): The canvas object where I'm drawing myself in

    shape (tuple): The shape of the image where I'm drawing mysel of top of.
      To be specified as ``(height, width)``.  This should correspond to the
      shape of the original image, **not** the shape of the zoomed image on
      the screen.

    points (:py:class:`numpy.ndarray`, Optional): A numpy array (or a list of
      lists) in which rows represent each point annotated and columns represent
      annotations in ``(y,x)`` format.  This should correspond to the original
      annotated coordinates, in integer precision.  The zooming factor is
      applied only for displaying purposes.

    zoom (float): The zoom level for the image. In case it is greater than 1.0,
      then the image will be zoomed in (increased in size). Otherwise, it will
      be zoomed out (reduced in size). Annotations will be taken relatively to
      the original image.  This setting only affects the displaying of images,
      the loading/saving of annotations.  Annotated values are temporarily
      stored in memory using actual coordinate (untransformed) values.

    active (:py:obj:`bool`, Optional): If set to ``True``, then makes this
      object look in active state.

    marker_radius (:py:obj:`int`, Optional): The number of pixels in the
      original image each annotation marker will occupy.

    pixel_skip (:py:obj:`int`, Optional): The number of pixels skipped every
      time the user uses a motion key with the Shift key pressed.

    mode (:py:obj:`str`, Optional): If the default object mode is "line" or
      "polygon"

  """

  def __init__(self, canvas, shape, points, zoom, active=False,
      marker_radius=1, pixel_skip=5, mode='line'):

    self.canvas = canvas  #canvas I'm drawn at
    self.image_height, self.image_width = shape  #shape of displayed image
    self.zoom = zoom  #zoom factor to applying when displaying
    self.marker_radius = marker_radius
    self.skip_factor = pixel_skip
    self.mode = mode
    self.active = True  #this will be changed later in this method

    # setup internal variables
    self.point = []
    self.widget = [] #the widgets related to the annotations
    self.decoration = [] #decorations, kept hidden for wigets

    # now add the points
    for k in points: self.append_point(k)

    # sets activation status
    if self.point:
      self._highlight_widget(-1)

    if not active:
      self.deactivate()


  def __len__(self):

    return len(self.point)


  def _make_cross(self, c):
    """Defines a cross + number in terms of a center and a radius"""

    logger.debug("Creating annotation display at (%d,%d)...", c[0], c[1])

    #create annotation with respect to zoomed image
    y, x = zoom_point(self.zoom, c)

    #points = (x, y-r, x, y+r, x, y, x-r, y, x+r, y, x, y)
    w = self.marker_radius
    w3 = 5*w;
    points = (
        x-w, y-w3,
        x+w, y-w3,
        x+w, y-w,
        x+w3, y-w,
        x+w3, y+w,
        x+w, y+w,
        x+w, y+w3,
        x-w, y+w3,
        x-w, y+w,
        x-w3, y+w,
        x-w3, y-w,
        x-w, y-w,
        )

    poly = self.canvas.create_polygon(points, outline='black',
        fill=COLOR_INACTIVE, tags="keypoint", width=1.0, state=tkinter.NORMAL)

    return poly


  def _make_hidden_label(self, point, text):
    """Creates hidden labels that can be displayed on demand"""

    # text - not modifiable for the color
    if x < (self.image_width/2): #first half along width
      if y < (self.image_height/2): #first half along height
        anchor = tkinter.NW
      else: #second half along height
        anchor = tkinter.SW
    else: #second half along width
      if y < (self.image_height/2): #first half along height
        anchor = tkinter.NE
      else: #second half along height
        anchor = tkinter.SE

    #create annotation with respect to zoomed image
    y, x = zoom_point(self.zoom, point)

    w = self.marker_radius
    w3 = 5*w;

    t = self.canvas.create_text((x-2*w3, y-2*w3), anchor=anchor,
        fill='black', tags="keypoint", state=tkinter.NORMAL,
        justify=tkinter.CENTER, text=' ' + text + ' ')

    bbox = self.canvas.bbox(t)
    self.canvas.itemconfig(t, state=tkinter.HIDDEN)

    # background "drop shadow" rectangle
    s = self.canvas.create_rectangle(bbox, fill=COLOR_INACTIVE,
        tags="annotation", state=tkinter.HIDDEN)
    # text on the top of the drop shadow
    self.canvas.tag_raise(t)

    return s, t


  def _deemphasize_widgets(self):
    """De-emphasizes (tone-down) all widgets for this object"""

    # make all other widgets inactive first
    for k in self.widget:
      self.canvas.itemconfig(k, fill=COLOR_INACTIVE)


  def _highlight_widget(self, k):
    """Highlights a given widget on the screen"""

    if not self.active: return
    self._deemphasize_widgets()
    self.canvas.itemconfig(self.widget[k], fill=COLOR_ACTIVE)


  def activate(self, p=None):
    """Makes the current widgets look "active"

    If a point ``p`` is passed in format ``(y,x)``, then it is used to search
    fora point and highlight that one.  Otherwise, highligths the last
    annotated point.
    """

    if self.active: return  #ignore

    self.active = True

    self._deemphasize_widgets()
    if self.point:
      hl = self._closest_annotation(p) if p else -1
      self._highlight_widget(hl)

    for k in self.decoration:
      if self.canvas.type(k) == 'line':
        self.canvas.itemconfig(k, fill=COLOR_INACTIVE)
      else: #polygon
        self.canvas.itemconfig(k, fill=COLOR_INACTIVE,
            outline=COLOR_INACTIVE)


  def deactivate(self):
    """Makes the current widgets look "inactive" """

    if not self.active: return  #ignore

    self.active = False

    # make all other widgets inactive first
    for k in self.widget:
      self.canvas.itemconfig(k, fill=COLOR_DESELECTED)

    for k in self.decoration:
      if self.canvas.type(k) == 'line':
        self.canvas.itemconfig(k, fill=COLOR_DESELECTED)
      else: #polygon
        self.canvas.itemconfig(k, fill=COLOR_DESELECTED,
            outline=COLOR_DESELECTED)


  def append_point(self, p):
    """Appends a new point ``(y,x)`` to the annotation object"""

    # add point
    self.point.append(p)
    self.widget.append(self._make_cross(p))
    self._highlight_widget(-1)
    self._update_decoration()


  def _closest_annotation(self, p):
    """Returns the closest possible annotation given the given location in
    ``(y,x)`` format
    """

    return numpy.argmin(scipy.spatial.distance.cdist(self.point,
      [unzoom_point(self.zoom, p)]))


  def insert_point(self, p):
    """Inserts the given annotation immediately, between two other

    The point ``p`` should be given in ``(y,x)`` format
    """

    # can't insert if no points are there...
    if not self.point: return

    closest_point = self._closest_annotation(p)
    self.point.insert(closest_point, p)

    self.widget.insert(closest_point, self._make_cross(p))

    # TODO: renumber all labels, so they are in the right order
    #for k, (_, _, t) in enumerate(self.widget):
    #  self.canvas.itemconfig(t, text=' ' + str(k) + ' ')

    self._highlight_widget(closest_point)
    self._update_decoration()


  def on_pointer_motion(self, p):
    """Constantly calculates where mouse is, update label that can be changed.

    The point should be supplied in ``(y,x)`` format
    """

    if not self.point: return
    self._highlight_widget(self._closest_annotation(p))


  def _delete_decoration(self):
    """Deletes the (polygon) mask for the current object"""

    if self.decoration:
      for widget in self.decoration:
        self.canvas.delete(widget)
    self.decoration = []


  def _create_decoration(self):
    """Creates decorations for the current object"""

    color = COLOR_INACTIVE if self.active else COLOR_DESELECTED

    if self.mode in ('polygon',):  #create a connector line

      if len(self.point) < 3:  #cannot create a polygon with 2 points...
        return

      points = [k for c in zoom_points(self.zoom, self.point) \
          for k in reversed(c)]
      self.decoration.append(self.canvas.create_polygon(*points,
          outline=color, fill=color, stipple="gray50",
          tags="mask", width=2.0, state=tkinter.HIDDEN))

    else:  #mode is line, create a connector between the points

      for k, p in enumerate(self.point[1:]):
        points = zoom_point(self.zoom, (self.point[k][1], self.point[k][0],
            self.point[k+1][1], self.point[k+1][0]))
        self.decoration.append(self.canvas.create_line(*points,
          fill=color, tags="mask", width=2.0, state=tkinter.HIDDEN))


  def toggle_mode(self):
    """Toggles current drawing mode between known modes

    This method will toggle the current mode between known operational modes
    (such as "line" and "polygon").  Internally, it just creates a hidden mask
    in case the mode is "polygon" and deletes it otherwise.
    """

    if self.mode in ('polygon',):
      self.mode = 'line'
    else:
      self.mode = 'polygon'

    self._update_decoration()


  def _update_decoration(self):
    """Updates the interpolated mask on the image"""

    self._delete_decoration()
    self._create_decoration()


  def _remove_widget(self, k):
    """Removes a given widget from the drawing"""

    widget = self.widget[k]
    self.widget.remove(widget)
    self.canvas.itemconfig(widget, state=tkinter.HIDDEN)
    self.canvas.delete(widget)


  def reset_zoom_factor(self, zoom):
    '''Resets the zoom factor and recreates all widgets'''

    # remove all widgets
    for k in range(len(self.point)):
      self._remove_widget(-1)

    # redraw widgets
    self.zoom = zoom
    for p in self.point:
      self.widget.append(self._make_cross(p))

    # reset activation status
    if self.active:
      self.active = False
      self.activate()
    else:
      self.active = True
      self.deactivate()

    self._update_decoration()


  def _remove_point(self, k):
    """Removes the active annotation"""

    if not self.point:
      return

    self.point.pop(k)
    self._remove_widget(k)

    if self.widget:
      self._highlight_widget(-1)

    self._update_decoration()


  def remove_active_point(self, p):
    """Removes the active point closest to point p in ``(y,x)`` format"""

    self._remove_point(self._closest_annotation(p))


  def _remove_last_point(self):
    """Removes the last annotation"""

    self._remove_point(-1)


  def remove_all_points(self):
    """Delete current frame annotations and reset the view"""

    for k in range(len(self.point)): self._remove_last_point()


  def show_decoration(self):
    """Shows extra decoration"""

    for w in self.decoration:
      self.canvas.itemconfig(w, state=tkinter.NORMAL)


  def hide_decoration(self):
    """Hides extra decoration"""

    for w in self.decoration:
      self.canvas.itemconfig(w, state=tkinter.HIDDEN)


  def move_active_point(self, p, key, state):
    """Moves the keypoint closes to ``p`` using the keyboard

    Parameters:

      p (tuple): point in ``(y, x)`` format

      key: the event keysim value (arrow keys, left right movement)

      state: the event state value (test for <SHIFT> key pressed)

    """

    if not self.point: return

    # move the object the appropriate amount
    dx, dy = (0, 0)
    if key in ('Right', 'l', 'L'): dx = 1
    elif key in ('Left', 'h', 'H'): dx = -1
    elif key in ('Up', 'k', 'K'): dy = -1
    elif key in ('Down', 'j', 'J'): dy = 1

    if state & SHIFT:
      dx *= self.skip_factor
      dy *= self.skip_factor

    closest_point = self._closest_annotation(p)
    (y, x) = self.point[closest_point]

    # if crosses the image border, than stop moving it
    if (y+dy) < 0 or (y+dy) >= self.image_height:
      dy = 0
    if (x+dx) < 0 or (x+dx) >= self.image_width:
      dx = 0

    self.point[closest_point] = (y+dy, x+dx)
    self.canvas.move(self.widget[closest_point], dx, dy)
    self._update_decoration()



class Tooltip(object):
  '''Creates a tooltip for a given widget as the mouse goes on it.

  see:

  http://stackoverflow.com/questions/3221956/
         what-is-the-simplest-way-to-make-tooltips-
         in-tkinter/36221216#36221216

  http://www.daniweb.com/programming/software-development/
         code/484591/a-tooltip-class-for-tkinter

  - Originally written by vegaseat on 2014.09.09.

  - Modified to include a delay time by Victor Zaccardo on 2016.03.25.

  - Modified
      - to correct extreme right and extreme bottom behavior,
      - to stay inside the screen whenever the tooltip might go out on
        the top but still the screen is higher than the tooltip,
      - to use the more flexible mouse positioning,
      - to add customizable background color, padding, waittime and
        wraplength on creation

    by Alberto Vassena on 2016.11.05.

    Tested on Ubuntu 16.04/16.10, running Python 3.5.2

  TODO: themes styles support
  '''

  def __init__(self, widget,
               *,
               bg='#FFFFEA',
               pad=(5, 3, 5, 3),
               text='widget info',
               waittime=800,
               wraplength=250):

    self.waittime = waittime  # in miliseconds, originally 500
    self.wraplength = wraplength  # in pixels, originally 180
    self.widget = widget
    self.text = text
    self.widget.bind("<Enter>", self.onEnter)
    self.widget.bind("<Leave>", self.onLeave)
    self.widget.bind("<ButtonPress>", self.onLeave)
    self.bg = bg
    self.pad = pad
    self.id = None
    self.tw = None


  def onEnter(self, event=None):

    self.schedule()


  def onLeave(self, event=None):

    self.unschedule()
    self.hide()


  def schedule(self):

    self.unschedule()
    self.id = self.widget.after(self.waittime, self.show)


  def unschedule(self):

      id_ = self.id
      self.id = None
      if id_:
          self.widget.after_cancel(id_)

  def show(self):

    def tip_pos_calculator(widget, label, *, tip_delta=(10, 5),
        pad=(5, 3, 5, 3)):

      w = widget

      s_width, s_height = w.winfo_screenwidth(), w.winfo_screenheight()

      width, height = (pad[0] + label.winfo_reqwidth() + pad[2],
          pad[1] + label.winfo_reqheight() + pad[3])

      mouse_x, mouse_y = w.winfo_pointerxy()

      x1, y1 = mouse_x + tip_delta[0], mouse_y + tip_delta[1]
      x2, y2 = x1 + width, y1 + height

      x_delta = x2 - s_width
      if x_delta < 0:
          x_delta = 0
      y_delta = y2 - s_height
      if y_delta < 0:
          y_delta = 0

      offscreen = (x_delta, y_delta) != (0, 0)

      if offscreen:

          if x_delta:
              x1 = mouse_x - tip_delta[0] - width

          if y_delta:
              y1 = mouse_y - tip_delta[1] - height

      offscreen_again = y1 < 0  # out on the top

      if offscreen_again:
          # No further checks will be done.

          # TIP:
          # A further mod might automagically augment the
          # wraplength when the tooltip is too high to be
          # kept inside the screen.
          y1 = 0

      return x1, y1


    bg = self.bg
    pad = self.pad
    widget = self.widget

    # creates a toplevel window
    self.tw = tkinter.Toplevel(widget)

    # Leaves only the label and removes the app window
    self.tw.wm_overrideredirect(True)

    win = tkinter.Frame(self.tw, background=bg, borderwidth=0)
    label = tkinter.Label(win,
        text=self.text,
        justify=tkinter.LEFT,
        background=bg,
        relief=tkinter.SOLID,
        borderwidth=0,
        wraplength=self.wraplength)

    label.grid(padx=(pad[0], pad[2]), pady=(pad[1], pad[3]),
        sticky=tkinter.NSEW)
    win.grid()

    x, y = tip_pos_calculator(widget, label)

    self.tw.wm_geometry("+%d+%d" % (x, y))


  def hide(self):

    tw = self.tw
    if tw:
      tw.destroy()
    self.tw = None


class ImageCarousel(tkinter.Canvas):
  """A sequence of images that can be displayed on a canvas


  Args:

    parent: (tkinter.Widget): A tkinter widget that will serve as parent to
      this canvas

    filelist (list): The input image file list

    zoom (:py:obj:`float`, Optional): The zoom level for the displayed image.
      In case it is greater than 1.0, then the image will be zoomed in
      (increased in size).  Otherwise, it will be zoomed out (reduced in size).
      Annotations will be taken relatively to the original image.  This setting
      only affects the displaying of images, the loading/saving of annotations.
      Annotated values are temporarily stored in memory using actual coordinate
      (untransformed) values.

    filter (:py:obj:`object`, Optional): A callable, that implements a
      filtering function for the image.  The filtering function should accept a
      :py:class:`PIL.Image.Image` as input (data type: is variable) and provide
      another Image as output, with the same specifications of the input image,
      in which the filter is applied

    args (dict): Extra parameters passed directly to the base
      :py:class:`tkinter.Canvas` object.

    kwargs (dict): Extra parameters passed directly to the base
      :py:class:`tkinter.Canvas` object.

  """


  def __init__(self, parent, filelist, zoom=None, filter=None, *args, **kwargs):

    self.filelist = filelist
    self.zoom = zoom
    self.filter = filter
    self.parent = parent

    # loads the current image, creates the image canvas
    self.curr_index = 0
    self.curr_original = self._load_pil_image(self.curr_index)
    self.curr_filtered = self._apply_zoom_filter(self.curr_original)
    self.curr_tk_image = ImageTk.PhotoImage(self.curr_filtered, Image.ANTIALIAS)

    super(ImageCarousel, self).__init__(parent, width=self.curr_filtered.width,
        height=self.curr_filtered.height, background='black',
        highlightthicknes=0, borderwidth=0, *args, **kwargs)

    self.curr_canvas_image = self.create_image(0, 0,
        anchor=tkinter.NW, image=self.curr_tk_image)

    self.bind("<Configure>", self._auto_reconfigure_zoom)


  def _auto_reconfigure_zoom(self, event=None):
    """Called when the user resets the window size (zoom recalibration)"""

    w, h = event.width, event.height
    zoom_x = float(w) / self.curr_original.width
    zoom_y = float(h) / self.curr_original.height
    self.zoom = min(zoom_x, zoom_y)
    logger.debug('Automatically setting zoom to %g', self.zoom)

    # no need to reload the current image, it has not changed
    self.curr_filtered = self._apply_zoom_filter(self.curr_original)
    self.curr_tk_image = ImageTk.PhotoImage(self.curr_filtered, Image.ANTIALIAS)
    self.config(width=self.curr_filtered.width, height=self.curr_filtered.height)
    self.itemconfig(self.curr_canvas_image, image=self.curr_tk_image)

    # trigger parent updates
    self.parent.reset_annotation_zoom(self.zoom)


  def reset_zoom_filter(self, zoom, filter):
    """Applies a new zoom-level to the existing image"""

    self.zoom = zoom
    self.filter = filter
    self._reset_to_image(self.curr_index)


  def _load_pil_image(self, pos):
    """Loads one of the images in internal file list, by position

    Args:

      pos (int): Index of image, inside ``self.filelist`` to load

    """

    bimg = bob.io.base.load(self.filelist[pos])

    # color images are transposed so they become like PIL's
    bimg = bob.io.image.utils.to_matplotlib(bimg)

    return Image.fromarray(bimg)


  def _apply_zoom_filter(self, image):
    """Applies zooming and filtering, if configured

    Args:

      image (PIL.Image): image that will be transformed

    """

    if self.zoom is not None:
      shape = zoom_point(self.zoom, (image.width, image.height))
      image = image.resize(shape, Image.ANTIALIAS)

    if self.filter is not None:
      image = self.filter(image)

    return image


  def _reset_to_image(self, pos):
    """Resets the canvas to load another image from the carousel"""

    self.curr_original = self._load_pil_image(self.curr_index)
    self.curr_filtered = self._apply_zoom_filter(self.curr_original)
    self.curr_tk_image = ImageTk.PhotoImage(self.curr_filtered, Image.ANTIALIAS)
    self.config(width=self.curr_filtered.width, height=self.curr_filtered.height)
    self.itemconfig(self.curr_canvas_image, image=self.curr_tk_image)


  def go_to_next_image(self):
    """Advances internal pointer to next image on the carousel"""

    self.curr_index += 1
    if self.curr_index >= len(self.filelist):
      self.curr_index = 0

    self._reset_to_image(self.curr_index)


  def go_to_previous_image(self):
    """Rewinds internal pointer to previous image on the carousel"""

    self.curr_index -= 1
    if self.curr_index < 0:
      self.curr_index = (len(self.filelist) - 1)

    self._reset_to_image(self.curr_index)


  def relative_pointer_position(self):
    """Returns the ``(y,x)`` current pointer position with respect to this
    canvas"""

    return (self.parent.winfo_pointery() - self.winfo_rooty(),
        self.parent.winfo_pointerx() - self.winfo_rootx())


  def pointer_is_outside_image(self):
    """Tells if an event is within this canvas window"""

    (y,x) = self.relative_pointer_position()
    return (y < 0) or (y >= self.curr_filtered.height) or \
        (x < 0) or (x >= self.curr_filtered.width)


  def current_filename(self):
    """Returns the current filename being displayed"""

    return self.filelist[self.curr_index]


  def current_index(self):
    """Returns the current index in the filelist being diplayed"""

    return self.curr_index


  def current_shape(self):
    """Returns the current shape in the format ``(y,x)``"""

    return (self.curr_filtered.height, self.curr_filtered.width)


  def original_shape(self):
    """Returns the original image shape in the format ``(y,x)``"""

    return (self.curr_original.height, self.curr_original.width)


  def __len__(self):
    """Returns the number of images in the carousel"""

    return len(self.filelist)


class Dialog(tkinter.Toplevel):
  """A pop-up window dialog - no internal objects"""


  def __init__(self, parent, shape):

    self.parent = parent
    super(Dialog, self).__init__()
    self.transient(self.parent)

    # this is where the dialog will appear
    self.geometry("%dx%d+%d+%d" % (shape[0], shape[1],
      parent.winfo_rootx()+50, parent.winfo_rooty()+50))

    self.lift()

    # binds return, escape and window-close actions to `self.on_close()`
    self.bind("<Return>", self.on_close)
    self.bind("<Escape>", self.on_close)
    self.protocol("WM_DELETE_WINDOW", self.on_close)


  def on_close(self, event=None):

    self.destroy()
    self.parent.update()
    self.parent.deiconify()


class HelpDialog(Dialog):
  """A pop-up specialization for the help message"""


  def __init__(self, parent, shape, text):

    super(HelpDialog, self).__init__(parent, shape)
    self.title('Help')

    # placeholder for the help text
    tbox = tkinter.Text(self, width=50, height=70)
    tbox.insert(tkinter.INSERT, text) #fill in contents
    tbox.grid(row=0, column=0, sticky=tkinter.NSEW)
    self.grid_rowconfigure(0, weight=1)
    self.grid_columnconfigure(0, weight=1)

    # scrollbar for the help text
    scrollbar = tkinter.ttk.Scrollbar(tbox)
    scrollbar.pack(side=tkinter.RIGHT, fill=tkinter.Y)
    tbox.config(yscrollcommand=scrollbar.set)
    scrollbar.config(command=tbox.yview)
    tbox.config(state=tkinter.DISABLED)

    # a single dismiss button
    btn = tkinter.ttk.Button(self, text ="Dismiss", command=lambda:
        self.on_close())
    btn.grid(row=1, column=0, sticky=tkinter.S)

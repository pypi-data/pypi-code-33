#!/usr/bin/env python
# vim: set fileencoding=utf-8 :

"""A keypoint annotation tool for images

This tool allows you to annotate batches of images using keypoints.  A keypoint
is placed everytime you click (left-mouse button) on the image being annotated.
The tool can be used to annotate single points and sequences of points making
up a line or a polygon.  This tool does not record the type of annotation, just
the keypoints are stored.  You can select during display the type of decoration
to use for highlighting the annotation (line or polygon).  In this sense, the
connections drawn and the polygon filling are just there for semantical
interpretation of hand-placed keypoints.

This tool treats any number of image inputs, one after the other.  As images
are loaded, annotations for the previous image are automatically saved on a
text file, following a simple format (y,x) keeping the order in which they
where inserted.

It is recommended you familiarize yourself with the keyboard and pointer (mouse
use is recommended) bellow so you can use this tool more efficiently.  A few
key actions are displayed on the left of the tool canvas and provides a faster
start for new users.

You can start this application in editing (default) or viewing mode.  If you
use it to view annotations only, you will not be able to edit the keypoints.


Keyboard shortcuts
------------------

``?``
  opens a dialog with this help message

``a | Zero | <KP_Zero>``
  places new point under pointer cursor, on the currently active (annotation)
  object

``i | <Shift>-Zero | <Shift>-KP_Zero``
  inserts new point on a currently active object, before the current active
  point

``d | <Del>``
  deletes the currently active point on the currently active object (marked in
  different color)

``o``
  edits the next object

``O``
  edits the previous object

``m``
  toogles current object between "polygon" and "line" modes

``c``
  creates a new (annotation) object

``D``
  deletes current (annotation) object

``X``
  deletes all annotated objects

``n``
  moves to the next image

``p``
  moves to the previous image

``s``
  saves current annotations

``q``
  quits the application, saving annotations for the current image

``<Alt>``
  Temporarily shows line connections or polygon decorations (while pressed)

``<Esc>``
  Quits the application **without saving**


Annotation movement
-------------------

.. note:: Only works with the last annotated point (or the one closest to
          pointer)

``h | Left``
  moves active annotation by 1 pixel to the left

``l | Right``
  moves active annotation by 1 pixel to the right

``k | Up``
  moves active annotation by 1 pixel up

``j | Down``
   moves active annotation by 1 pixel down

``<Shift> + motion keys``
  moves active annotation by 5 pixels on that direction


Pointer shortcuts
-----------------

.. note:: Tested with a mouse.  Trackpads do not normally offer these keys.

``<Left>``
  places new annotation under the pointer cursor

``<Shift>-<Left>``
  inserts new annotation before the current annotation

``<Right>``
  deletes the currently active annotation

``<Wheel Down>``
  moves to the next image

``<Wheel Up>``
  moves to the previous image

"""


import os
import math
import tkinter
import tkinter.ttk
import tkinter.font
import functools
import warnings

import numpy
from PIL import Image
import skimage
import skimage.exposure

from . import io
from . import widgets

import logging
logger = logging.getLogger(__name__)


class AnnotatorApp(tkinter.Tk):
  """A wrapper for the annotation application

  Parameters:

    images (str): A base directory where I am going to search for
      images

    extension (str): The extension to use when searching for images inside the
      ``images`` folder

    annotations (str): Base directory where annotations are going to be saved

    readonly (:py:obj:`bool`, Optional): If set to ``True``, then does not
      allow the creation of and deletion of annotations. Saving is also
      disabled.

    zoom (:py:obj:`float`, Optional): The zoom level for the image. In case it
      is greater than 1.0, then the image will be zoomed in (increased in
      size). Otherwise, it will be zoomed out (reduced in size). Annotations
      will be taken relatively to the original image.  This setting only
      affects the displaying of images, the loading/saving of annotations.
      Annotated values are temporarily stored in memory using actual coordinate
      (untransformed) values.

    marker_radius (:py:obj:`int`, Optional): The number of pixels in the
      original image each annotation marker will occupy.

    pixel_skip (:py:obj:`int`, Optional): The number of pixels skipped every
      time the user uses a motion key with the Shift key pressed.

    default_mode (:py:obj:`str`, Optional): If the default object mode
      during object creation is "line" or "polygon"

  """

  def __init__(self, images, extension, annotations, readonly=False, zoom=1.0,
      marker_radius=1, pixel_skip=5, default_mode = 'line', *args, **kwargs):

    super(AnnotatorApp, self).__init__(*args, **kwargs)
    self.title("annotate")

    self.basedir = images
    self.filelist = io.find(self.basedir, '*%s' % extension)
    logger.info('Loading %d images files found on %s', len(self.filelist),
        images)

    self.outputdir = annotations
    self.readonly = readonly
    self.zoom = zoom
    self.marker_radius = marker_radius
    self.skip_factor = pixel_skip
    self.default_mode = default_mode

    # setup internal variables
    self.curr_annotation = None #the currently annotated object
    self.annotation = [] #annotations existing on the current image
    self.filter = False

    # builds the application interface - buttons, frames and the image canvas
    self.frames = {}
    self.buttons = {}
    self.labels = {}
    self.variables = {}
    self.tooltips = {}
    self.canvas = None  #where the image will be displayed

    f = self.frames['left'] = tkinter.ttk.Frame(self)
    f.pack(side=tkinter.LEFT, padx=5, pady=5, fill=tkinter.Y, expand=False)

    # creates a little panel for information and buttons, on the left
    f = self.frames['image-selector'] = tkinter.ttk.LabelFrame(f, text="Images")
    f.grid(row=0, sticky=tkinter.NSEW)

    v = self.variables['image-progress'] = tkinter.StringVar()
    v.set('[progress]')
    l = self.labels['image-progress'] = tkinter.ttk.Label(f, textvariable=v)
    l.grid(row=0, columnspan=2)

    b = self.buttons['previous-frame'] = tkinter.ttk.Button(f, text="<< (p)",
        command=self.previous_frame)
    b.grid(row=1, column=0, sticky=tkinter.NSEW)
    self.tooltips['previous-frame'] = \
        widgets.Tooltip(b, text='Go to previous image (keyboard: p)')

    b = self.buttons['next-frame'] = tkinter.ttk.Button(f, text=">> (n)",
        command=self.next_frame)
    b.grid(row=1, column=1, sticky=tkinter.NSEW)
    self.tooltips['next-frame'] = \
        widgets.Tooltip(b, text='Go to next image (keyboard: n)')

    f = self.frames['annotations'] = tkinter.ttk.LabelFrame(self.frames['left'],
        text="Objects")
    f.grid(row=1, sticky=tkinter.NSEW)

    v = self.variables['annotation-progress'] = tkinter.StringVar()
    v.set('[progress]')
    l = self.labels['annotation-progress'] = tkinter.ttk.Label(f,
        textvariable=v)
    l.grid(row=0, columnspan=2)

    b = self.buttons['previous-annotation'] = \
        tkinter.ttk.Button(f, text="<< (O)",
            command=self.activate_previous_annotation)
    b.grid(row=1, column=0, sticky=tkinter.NSEW)
    self.tooltips['previous-annotation'] = widgets.Tooltip(b,
        text='Highlight (edit) previous object (keyboard: O)')

    b = self.buttons['next-annotation'] = tkinter.ttk.Button(f, text=">> (o)",
        command=self.activate_next_annotation)
    b.grid(row=1, column=1, sticky=tkinter.NSEW)
    self.tooltips['next-annotation'] = widgets.Tooltip(b,
        text='Highlight (edit) next object (keyboard: o)')

    b = self.buttons['create-object'] = tkinter.ttk.Button(f,
        text="new (c)", command=self.create_new_annotation)
    b.grid(row=2, column=0, sticky=tkinter.NSEW)
    self.tooltips['create-object'] = widgets.Tooltip(b,
        text='Annotate a new object (keyboard: c)')

    b = self.buttons['delete-object'] = tkinter.ttk.Button(f,
        text="del (D)", command=self.remove_active_annotation)
    b.grid(row=2, column=1, sticky=tkinter.NSEW)
    self.tooltips['create-object'] = widgets.Tooltip(b,
        text='Remove active object (keyboard: D)')

    v = self.variables['decoration-mode'] = tkinter.StringVar()
    v.set('mode (m): %s' % self.default_mode[:4].upper())
    b = self.buttons['toggle-mode'] = tkinter.ttk.Button(f, textvariable=v,
        command=self.toggle_active_annotation_mode)
    b.grid(row=3, columnspan=2, sticky=tkinter.NSEW)
    self.tooltips['decoration-mode'] = widgets.Tooltip(b,
        text='Toggle between ALT decoration modes.  This is no way ' \
            'affects annotation results (keyboard: m)')

    v = self.variables['annotation-numpoints'] = tkinter.StringVar()
    v.set('points')
    l = self.labels['annotation-numpoints'] = tkinter.ttk.Label(f,
        textvariable=v)
    l.grid(row=4, columnspan=2)
    self.tooltips['decoration-mode'] = widgets.Tooltip(l,
        text='Displays the number of annotated points in the current ' \
            'object being annotated (highlit)')

    f = self.frames['filters'] = tkinter.ttk.LabelFrame(self.frames['left'],
        text="Filters")
    f.grid(row=2, sticky=tkinter.NSEW)

    v = self.variables['adaheq'] = tkinter.IntVar()
    v.set(0)
    b = self.buttons['adaheq'] = tkinter.ttk.Checkbutton(f,
        text="CLAHE", command=self.toggle_filter, variable=v)
    b.grid(row=0, columnspan=3, sticky=tkinter.W)
    self.tooltips['adaheq'] = widgets.Tooltip(b,
        text='Applies Contrast Limited Adaptive Histogram Equalization ' \
            '(CLAHE) to the displayed image. You can finetune parameters ' \
            'on the text boxes below')

    v = self.variables['adaheq-kernel-size'] = tkinter.IntVar()
    v.set(18)
    l = self.labels['adaheq-kernel-size'] = tkinter.ttk.Label(f, text='Kernel:')
    l.grid(row=1, column=1, sticky=tkinter.E)
    b = self.buttons['adaheq-kernel-size'] = tkinter.ttk.Entry(f,
        textvariable=v, width=4)
    b.grid(row=1, column=2, sticky=tkinter.E)

    v = self.variables['adaheq-clip'] = tkinter.DoubleVar()
    v.set(0.02)
    l = self.labels['adaheq-clip'] = tkinter.ttk.Label(f, text='Clip:')
    l.grid(row=2, column=1, sticky=tkinter.W)
    b = self.buttons['adaheq-clip'] = tkinter.ttk.Entry(f, textvariable=v,
        width=4)
    b.grid(row=2, column=2, sticky=tkinter.W)

    f = self.frames['pointer'] = tkinter.ttk.LabelFrame(self.frames['left'],
        text="Pointer [x, y]")
    f.grid(row=3, sticky=tkinter.NSEW)

    v = self.variables['pointer-position'] = tkinter.StringVar()
    v.set('(0, 0)')
    l = self.labels['pointer-position'] = tkinter.ttk.Label(f, textvariable=v)
    l.grid(row=0, sticky=tkinter.E)
    self.tooltips['pointer-position'] = widgets.Tooltip(l,
        text='This box displays the current pointer position with respect ' \
            'to the displayed image. Coordinates are displayed in true ' \
            'image resolution')

    f = self.frames['zoom'] = tkinter.ttk.LabelFrame(self.frames['left'],
        text="Zoom")
    f.grid(row=4, sticky=tkinter.NSEW)

    v = self.variables['zoom'] = tkinter.StringVar()
    v.set('%g' % self.zoom)
    l = self.labels['zoom'] = tkinter.ttk.Label(f, textvariable=v)
    l.grid(row=0, sticky=tkinter.E)
    self.tooltips['zoom'] = widgets.Tooltip(l,
        text='This box displays the current image zoom.')

    f = self.frames['help'] = tkinter.ttk.LabelFrame(self.frames['left'],
        text="Help")
    f.grid(row=5, sticky=tkinter.NSEW)

    b = self.buttons['display-help'] = \
        tkinter.ttk.Button(f, text='help (?)', command=self.on_help)
    b.grid(row=0, sticky=tkinter.E)
    self.tooltips['display-help'] = widgets.Tooltip(b,
        text='Click on this button to display the help dialog and ' \
            'learn more about keyboard and mouse-based shortcuts')

    # creates the image canvas on the root window
    self.canvas = widgets.ImageCarousel(self, self.filelist, zoom=self.zoom,
        filter=None)
    self.canvas.pack(side=tkinter.TOP, padx=0, pady=0, expand=1,
        fill=tkinter.BOTH)

    # adds keyboard/pointer bindings
    self._add_bindings()

    # finally, loads annotations available for current image
    self._load_annotations()


  def _rebuild_interface(self):
    """Updates the displayed interface"""

    # setup filter function
    filter_function = None
    if self.filter:

      def _clahe(img, kernel, clip):
        nimg = numpy.array(img)
        nr = math.ceil(nimg.shape[0] / kernel)
        nc = math.ceil(nimg.shape[1] / kernel)
        with warnings.catch_warnings():
          warnings.simplefilter("ignore")
          nimg2 = skimage.exposure.equalize_adapthist(nimg, kernel_size=(nr,
            nc), clip_limit=clip)
          if nimg.dtype == numpy.uint8:
            nimg2 = skimage.img_as_ubyte(nimg2)
          elif nimg.dtype == numpy.uint16:
            nimg2 = skimage.img_as_uint(nimg2)
        return Image.fromarray(nimg2)

      filter_function = functools.partial(_clahe,
          kernel=self.variables['adaheq-kernel-size'].get(),
          clip=self.variables['adaheq-clip'].get(),
          )

    self.canvas.reset_zoom_filter(self.zoom, filter_function)
    self._load_annotations()
    self._update_status()


  def reset_annotation_zoom(self, zoom):
    """Resets the zoom of each annotation"""

    self.zoom = zoom
    for k in self.annotation:
      k.reset_zoom_factor(self.zoom)

    self._update_status()


  def _load_annotations(self):
    """Loads annotations for the currently active image"""

    # remove all annotations, if any exist
    for k in range(len(self.annotation)):
      p = self.annotation.pop()
      p.remove_all_points()

    # load data from annotation file, if it exists
    stem = os.path.relpath(self.canvas.current_filename(), self.basedir)
    candidate_annotation = os.path.join(self.outputdir, stem)
    candidate_annotation = os.path.splitext(candidate_annotation)[0] + '.json'

    if os.path.exists(candidate_annotation):
      data = io.load(candidate_annotation)
      for k in data:
        if not k: continue
        self.annotation.append(widgets.Annotation(self.canvas,
          self.canvas.original_shape(), k, self.zoom, False,
          self.marker_radius, self.skip_factor, self.default_mode))

      if self.annotation:
        self.annotation[-1].activate()
        self.curr_annotation = self.annotation[-1]

    if not self.annotation:  #creates a first annotation object with no points
      self.create_new_annotation()


  def _canvas_pointer_position(self):
    """Returns the relative position of the pointer w.r.t. canvas"""

    return self.canvas.relative_pointer_position()


  def _update_status(self):

    self.variables['image-progress'].set('#%d out of %d' % (
      self.canvas.current_index()+1, len(self.canvas)))
    self.variables['annotation-numpoints'].set('#%d: %d point%s' % \
        (self.annotation.index(self.curr_annotation)+1,
        len(self.curr_annotation), '' if len(self.curr_annotation)==1 else 's'))
    self.variables['annotation-progress'].set('#%d out of %d' % (
      self.annotation.index(self.curr_annotation)+1, len(self.annotation)))

    # set the window title
    stem = os.path.relpath(self.canvas.current_filename(), self.basedir)
    self.title("annotate: %s (%d/%d) [%s]" % (stem,
      self.canvas.current_index()+1, len(self.canvas),
      'viewing' if self.readonly else 'editing'))

    # set the current pointer position, relative to the image
    y, x = widgets.unzoom_point(self.zoom, self._canvas_pointer_position())
    self.variables['pointer-position'].set('(%d, %d)' % (x, y))

    # sets the zoom level
    self.variables['zoom'].set('%g' % self.zoom)


  def save(self, *args, **kwargs):
    """Action executed when we need to save the current annotations"""

    if self.readonly:
      logger.debug('In read-only mode: saving skipped')
      return

    stem = os.path.relpath(self.canvas.current_filename(), self.basedir)
    stem = os.path.splitext(stem)[0] + '.json'
    output_path = os.path.join(self.outputdir, stem)
    output_dir = os.path.dirname(output_path)

    if not os.path.exists(output_dir):
      os.makedirs(output_dir)

    data = [k.point for k in self.annotation]

    if any(data) and not self.readonly:
      io.save(data, output_path, backup=True)
      logger.info('Saved `%s\'', output_path)

    else:
      logger.debug('No annotations to save at `%s\'', output_path)


  def on_quit_no_saving(self, *args, **kwargs):
    """On quit we either dump the output to screen or to a file."""

    data = [k.point for k in self.annotation]

    if any(data) and not self.readonly:
      stem = os.path.relpath(self.canvas.current_filename(), self.basedir)
      logger.warn("Maybe lost annotations for %s", stem)

    self.destroy()


  def on_quit(self, *args, **kwargs):
    """On quit we either dump the output to screen or to a file."""

    if not self.readonly:
      self.save(*args, **kwargs)
      if self.annotation:
        logger.info("Saved all annotations, bye!")
      else:
        logger.info("No annotations to save, bye!")

    self.destroy()


  def on_help(self, event=None):
    """Creates a help dialog box with the currently enabled commands"""

    self.withdraw()
    dialog = widgets.HelpDialog(self, (600, 700), __doc__)


  def previous_frame(self, event=None):
    """Rewinds to the previous frame, wraps around if needed"""

    self.save()
    self.canvas.go_to_previous_image()
    self._load_annotations()


  def next_frame(self, event=None):
    """Advances to the next frame, wraps around if needed"""

    self.save()
    self.canvas.go_to_next_image()
    self._load_annotations()


  def on_pointer_motion(self, event):
    """Constantly calculates where pointer is, update label that can be
    changed"""

    self._update_status()
    self.curr_annotation.on_pointer_motion(self._canvas_pointer_position())


  def append_point_on_active_annotation(self, event):
    """Adds the given annotation position immediately"""

    # ignore random events outside the drawing window
    if self.canvas.pointer_is_outside_image(): return

    y, x = widgets.unzoom_point(self.zoom, self._canvas_pointer_position())
    logger.debug('Appending point %d (%d, %d) to object %d...',
      len(self.curr_annotation), y, x,
      self.annotation.index(self.curr_annotation))
    self.curr_annotation.append_point((y, x))
    self._update_status()


  def insert_point_on_active_annotation(self, event):
    """Inserts the given annotation position immediately, between two other"""

    # ignore random events outside the drawing window
    if self.canvas.pointer_is_outside_image(): return

    y, x = widgets.unzoom_point(self.zoom, self._canvas_pointer_position())
    logger.debug('Inserting point %d (%d, %d) to object %d...',
      len(self.curr_annotation), y, x,
      self.annotation.index(self.curr_annotation))
    self.curr_annotation.insert_point((y, x))
    self._update_status()


  def remove_point_from_active_annotation(self, event):
    """Removes the active point under the currently active annotation"""

    y, x = self._canvas_pointer_position()
    self.curr_annotation.remove_active_point((y, x))
    self._update_status()


  def remove_active_annotation(self, event=None):
    """Removes all points under the currently active annotation"""

    logger.info('Removing active annotation...')
    self.annotation.remove(self.curr_annotation)
    self.curr_annotation.remove_all_points()
    if not self.annotation:
      self.create_new_annotation()
    self.curr_annotation = self.annotation[-1]
    self.curr_annotation.activate()
    self._update_status()


  def remove_all_annotations(self, event=None):
    """Delete all current annotation and reset the view"""

    logger.info('Removing all annotations...')
    for k in range(len(self.annotation)):
      p = self.annotation.pop()
      p.remove_all_points()
    self.create_new_annotation()  # adds a new base annotation object


  def on_show_all(self, event):
    """Shows all elements"""

    logger.debug('Showing all...')
    for k in self.annotation: k.show_decoration()


  def on_hide_all(self, event):
    """Hides all elements"""

    logger.debug('Hiding all...')
    for k in self.annotation: k.hide_decoration()


  def move_active_annotation(self, event):
    """Moves the last annotated keypoint using the keyboard"""

    y, x = self._canvas_pointer_position()
    self.curr_annotation.move_active_point((y, x), event.keysym, event.state)
    self._update_status()


  def activate_next_annotation(self, event=None):
    """Activates (for editing, possibly) the next object - wraps around"""

    if not self.annotation: return
    self.curr_annotation.deactivate()
    current = self.annotation.index(self.curr_annotation)
    if current == (len(self.annotation)-1):
      current = 0
    else:
      current += 1
    self.curr_annotation = self.annotation[current]
    self.curr_annotation.activate()
    self._update_status()


  def activate_previous_annotation(self, event=None):
    """Activates (for editing, possibly) the previous object - wraps around"""

    if not self.annotation: return
    self.curr_annotation.deactivate()
    current = self.annotation.index(self.curr_annotation)
    if current == 0:
      current = -1
    else:
      current -= 1
    self.curr_annotation = self.annotation[current]
    self.curr_annotation.activate()
    self._update_status()


  def create_new_annotation(self, event=None):
    """Creates a new annotation, make it active"""

    if self.curr_annotation: self.curr_annotation.deactivate()
    self.annotation.append(widgets.Annotation(self.canvas,
      self.canvas.original_shape(), [], self.zoom, True, self.marker_radius,
      self.skip_factor, self.default_mode))
    self.curr_annotation = self.annotation[-1]
    self._update_status()


  def toggle_active_annotation_mode(self, event=None):

    for k in self.annotation: k.toggle_mode()
    self.default_mode = 'line' if self.default_mode == 'polygon' else 'polygon'
    self.variables['decoration-mode'].set('mode (m): %s' % \
        self.default_mode[:4].upper())
    self._update_status()


  def toggle_filter(self, event=None):
    """Togglers filter/no-filter on the displayed image"""

    if self.filter:
      self.filter = False
      self._rebuild_interface()
    else:
      self.filter = True
      self._rebuild_interface()


  def _add_bindings(self):
    """Adds pointer bindings to the given widget"""

    # add a given annotation (marked in white)
    if not self.readonly:
      self.bind("a", self.append_point_on_active_annotation)
      self.bind("i", self.insert_point_on_active_annotation)
      self.bind("<Shift-a>", self.insert_point_on_active_annotation)
      self.bind("<Insert>", self.insert_point_on_active_annotation)
      self.bind("0", self.append_point_on_active_annotation)
      self.bind("<Shift-0>", self.insert_point_on_active_annotation)
      self.bind("<Shift-KP_0>", self.insert_point_on_active_annotation)
      self.bind("<KP_0>", self.append_point_on_active_annotation)
      self.bind("<Button-1>", self.append_point_on_active_annotation)
      self.bind("<Shift-Button-1>", self.insert_point_on_active_annotation)
      self.bind("d", self.remove_point_from_active_annotation)
      self.bind("<Delete>", self.remove_point_from_active_annotation)
      self.bind("D", self.remove_active_annotation)
      self.bind("X", self.remove_all_annotations)
      self.bind("<Button-3>", self.remove_point_from_active_annotation)
      self.bind("c", self.create_new_annotation)

    self.bind("o", self.activate_next_annotation)
    self.bind("O", self.activate_previous_annotation)
    self.bind("m", self.toggle_active_annotation_mode)
    self.bind("n", self.next_frame)
    self.bind("p", self.previous_frame)
    self.bind("N", self.next_frame)
    self.bind("P", self.previous_frame)
    self.bind("<Button-4>", self.previous_frame)
    self.bind("<Button-5>", self.next_frame)

    # keeps track of pointer coordinates
    self.bind("<Motion>", self.on_pointer_motion)

    # motion keys - move frame or keypoint depending on keypoint focus
    if not self.readonly:
      self.bind("<Right>", self.move_active_annotation)
      self.bind("<Shift-Right>", self.move_active_annotation)
      self.bind("<Left>", self.move_active_annotation)
      self.bind("<Shift-Left>", self.move_active_annotation)
      self.bind("<Up>", self.move_active_annotation)
      self.bind("<Shift-Up>", self.move_active_annotation)
      self.bind("<Down>", self.move_active_annotation)
      self.bind("<Shift-Down>", self.move_active_annotation)
      self.bind("h", self.move_active_annotation)
      self.bind("H", self.move_active_annotation)
      self.bind("l", self.move_active_annotation)
      self.bind("L", self.move_active_annotation)
      self.bind("k", self.move_active_annotation)
      self.bind("K", self.move_active_annotation)
      self.bind("j", self.move_active_annotation)
      self.bind("J", self.move_active_annotation)

    # hide all with Right-Alt pressed
    self.bind("<KeyPress-Alt_L>", self.on_show_all)
    self.bind("<KeyRelease-Alt_L>", self.on_hide_all)
    self.bind("<KeyPress-Alt_R>", self.on_show_all)
    self.bind("<KeyRelease-Alt_R>", self.on_hide_all)

    self.bind("?", self.on_help)

    # Capture closing the app -> use to save the file
    self.protocol("WM_DELETE_WINDOW", self.on_quit)
    self.bind("q", self.on_quit)
    self.bind("<Escape>", self.on_quit_no_saving)
    self.bind("s", self.save)

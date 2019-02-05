#!/usr/bin/env python
# vim: set fileencoding=utf-8 :

import os

import click
from bob.extension.scripts.click_helper import verbosity_option, \
    ResourceOption

@click.command(epilog='''
Examples:

  Annotate all images (ending in ".png") from "images" directory (scanned
  recursively), put annotations in the current work directory, following the
  same directory structure:

    $ bob annotate -v images

  Annotate all images (ending in ".png") from "images" directory (scanned
  recursively), put annotations in the "annotations" directory (that is created
  if it does not already exists), following the same directory structure:

    $ bob annotate -v images annotations

  Annotate the image of Lena, with a 2x zoom, get the result in `lenna.json`:

    $ bob annotate -v --zoom=2 bob/ip/annotator/data

  Visualize annotations for Lena, with a 0.5x zoom, from the file `lenna.json`:

    $ bob annotate -v --readonly --zoom=0.5 bob/ip/annotator/data
''')
@click.argument('images', required=True, type=click.Path(file_okay=False,
  dir_okay=True, writable=False, readable=True, exists=True))
@click.argument('annotations', required=False, type=click.Path(file_okay=False,
  dir_okay=True, writable=True, readable=True, exists=False))
@click.option('-e', '--extension', default='.png',
    show_default=True, help='The type of files to look for on the images' \
        'directory')
@click.option('-z', '--zoom', default=1.0, type=click.FLOAT,
    show_default=True, help='The zoom-level to apply for images.  Choosing' \
        'a value larger than 1.0 increases the app window size.  If you ' \
        'choose a value smaller than 1.0, it decreases it.  Use this ' \
        'setting to adjust window size on your screen')
@click.option('-r', '--readonly/--no-readonly', default=False,
    help='Set this avoid any changes to existing annotations')
@verbosity_option(cls=ResourceOption)
def annotate(images, annotations, extension, zoom, readonly, verbose):
  """A TkInter-based keypoint annotation tool for images"""

  if annotations is None:
    # if the user did not specify location, use the current directory
    annotations = os.path.realpath(os.curdir)

  from ..gui import AnnotatorApp
  app = AnnotatorApp(images, extension, annotations, readonly, zoom)
  app.mainloop()

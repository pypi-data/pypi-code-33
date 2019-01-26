import sys, io

# Requires pygments

class Colorizer(object):

  def __init__(self, style, debug=False, return_content=False):
    self.style = style
    self.debug = debug
    self.output = ''
    self.return_content = return_content

  def colorize_exception_traceback(self, value, tb):
    import traceback
    import pygments.lexers

    # Get the text
    # As of Python 3.5, the _type param is ignored, and is instead inferred from 'value'.
    # See notes in https://docs.python.org/3/library/traceback.html#traceback.print_exception
    tb_text = "".join(traceback.format_exception(None, value, tb))


    # Format the text
    lexer = pygments.lexers.get_lexer_by_name("py3tb", stripall=True)
    tb_colored = pygments.highlight(tb_text, lexer, self.formatter)

    self.write(tb_colored)

    return self.output if self.return_content else None


  # Utility function to print the current traceback in color.
  def print_current_stack(self, omit_frames=0):
    # Get the current traceback list (can't seem to get the traceback object - maybe only for exceptions?)
    import traceback
    tb_extracted_list = traceback.extract_stack()
    return self.colorize_traceback_list(tb_extracted_list, omit_frames)


  # Utility function to print a given traceback LIST in color.
  def colorize_traceback_list(self, tb, omit_frames=0):
    import traceback
    import pygments.lexers

    # Determine how many frames to drop
    actual_omit_frames = omit_frames + 1  # Whatever the caller requested, plus this function.

    # Get the text
    tb_extracted = traceback.extract_stack()
    tb_extracted = tb_extracted[:-(actual_omit_frames)]
    tb_text = "".join(traceback.format_list(tb_extracted))

    # tb_text = traceback.format_tb(tb)

    # Format the text
    lexer = pygments.lexers.get_lexer_by_name("py3tb", stripall=True)
    tb_colored = pygments.highlight(tb_text, lexer, self.formatter)

    self.write(tb_colored)

    return self.output if self.return_content else None


  # Write to the stream, unless we have a logger attached.
  # In some contexts we can't write to stdout and have to send it through the logging infrastructure.
  def write(self, content):
    if self.return_content:
      self.output += content
    else:
      self.stream.write(content)


  @property
  def formatter(self):

    colors = self._get_term_color_support()

    if self.debug:
      sys.stderr.write("Detected support for %s colors\n" % colors)
    if colors == 256:
      fmt_options = {'style': self.style}
    elif self.style in ('light', 'dark'):
      fmt_options = {'bg': self.style}
    else:
      fmt_options = {'bg': 'dark'}
    from pygments.formatters import get_formatter_by_name
    import pygments.util
    fmt_alias = 'terminal256' if colors == 256 else 'terminal'

    try:
      return get_formatter_by_name(fmt_alias, **fmt_options)
    except pygments.util.ClassNotFound as ex:
      if self.debug:
        sys.stderr.write(str(ex) + "\n")
      return get_formatter_by_name(fmt_alias)

  @property
  def stream(self):
    try:
      import colorama
      return colorama.AnsiToWin32(sys.stderr)
    except ImportError:
      return sys.stderr


  def _get_term_color_support(self):
    try:
      import curses
    except ImportError:
      # Probably Windows, which doesn't have great curses support
      return 16

    # In the IPython kernel shell channel, any messages to stdout will kill the existing thread.
    # curses.setupterm sends some init codes to stdout.
    try:
      curses.setupterm()
      return curses.tigetnum('colors')
    except io.UnsupportedOperation:
      self.write(f'Note: Unable to call curses.setupterm support, defaulting to 256 colors.\n')

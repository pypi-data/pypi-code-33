import logging, collections
import pprint

# Optional Markdown display when in notebook mode
from .notebook import in_ipynb
from IPython.display import Markdown, display

BLACK, RED, GREEN, YELLOW, BLUE, MAGENTA, CYAN, WHITE = range(8)


# The background is set with 40 plus the number of the color, and the foreground with 30
# These are the sequences need to get colored output
RESET_SEQ = "\033[0m"
COLOR_SEQ = "\033[1;%dm"
BOLD_SEQ = "\033[1m"


def formatter_message(message, use_color = True):
  if use_color:
    message = message.replace("$RESET", RESET_SEQ).replace("$BOLD", BOLD_SEQ)
  else:
    message = message.replace("$RESET", "").replace("$BOLD", "")
  return message

COLORS = {
  'WARNING': YELLOW,
  'INFO': WHITE,
  'DEBUG': BLUE,
  'CRITICAL': YELLOW,
  'ERROR': RED
}

# Old format: '%(levelname)s: - %(name)s: %(message)s'
FORMAT = "[%(levelname)-5s][%(asctime)s][$BOLD%(name)-10s$RESET] %(message)s ($BOLD%(filename)s$RESET:%(lineno)d)"
COLOR_FORMAT = formatter_message(FORMAT, True)


# FORMAT_DEV = "[%(levelname)-5s] %(message)s ($BOLD%(filename)s$RESET:%(lineno)d)"
FORMAT_DEV = "[%(levelname)-5s] %(message)s"
COLOR_FORMAT_DEV = formatter_message(FORMAT_DEV, True)


class ColoredFormatter(logging.Formatter):
  def __init__(self, *args, **kwargs):
    self.colors_dict = { color: True for color in COLORS }  # Perf
    super().__init__(*args, **kwargs)

  def format(self, record):
    levelname = record.levelname
    if levelname in self.colors_dict:
      levelname_color = COLOR_SEQ % (30 + COLORS[levelname]) + levelname + RESET_SEQ
      record.levelname = levelname_color
    return logging.Formatter.format(self, record)


# https://stackoverflow.com/questions/3118059/how-to-write-custom-python-logging-handler
class MarkdownHandler(logging.StreamHandler):

  def __init__(self, *args, **kwargs):
    self.in_ipynb = in_ipynb()
    super().__init__(*args, **kwargs)

  def emit(self, record):
    try:
      markdown = hasattr(record, 'markdown')

      if markdown and self.in_ipynb:
        heading = getattr(record, 'heading', 0)
        heading_str = '#' * heading + ' '
        display( Markdown(heading_str + record.msg) )
      else:
        msg = self.format(record)
        self.stream.write(msg)
        self.stream.write(self.terminator)

      self.flush()
    except (KeyboardInterrupt, SystemExit):
      raise
    except:  # pylint: disable=bare-except
      self.handleError(record)

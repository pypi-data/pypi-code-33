### NOTE: This file should only have functions and not inherit anything from settings
### (or else it will have a circular dependency)
import pprint
import sys, logging, traceback
from colorama import Fore, Back, Style

from .colorizer import Colorizer


# CGT-TB (shows function call values and call stack context)
# https://docs.python.org/3/library/cgitb.html
# https://pymotw.com/2/cgitb/
if False:
  import cgitb
  cgitb.enable(format='text')


""" Developer tool to turn on automatic HTTP request logging.
Super useful for writing mocks for API libraries.
See http://stackoverflow.com/questions/10588644/how-can-i-see-the-entire-http-request-thats-being-sent-by-my-python-application
"""

## To use, uncomment, import requests at the top, and add requests to requirements.txt.

# Note: this doesn't actually log the request or response body. To do that, you need to add these lines to
# your virtualenv copy of requests/sessions.py, at the end of the 'def requests' method where the response is available.
# There isn't a published way of officially logging this yet.
#   pprint.pprint (vars(resp))
def enable_http_tracing():
  # These two lines enable debugging at httplib level (requests->urllib3->http.client)
  # You will see the REQUEST, including HEADERS and DATA, and RESPONSE with HEADERS but without DATA.
  # The only thing missing will be the response.body which is not logged.
  try:
    import http.client as http_client
  except ImportError:
      # Python 2
    import httplib as http_client
  http_client.HTTPConnection.debuglevel = 1

  # You must initialize logging, otherwise you'll not see debug output.
  # Note - if logging has already been configured, the basicConfig call will be a no-op.
  logging.basicConfig()
  logging.getLogger().setLevel(logging.DEBUG)
  requests_log = logging.getLogger("requests.packages.urllib3")
  requests_log.setLevel(logging.DEBUG)
  requests_log.propagate = True






original_hook = sys.excepthook

# Doesn't seem to work when running unit tests. (!)
LAUNCH_IPDB = False
PRINT_EXCEPTION_LOCALS = False

# If launch_ipdb is true, the exception hook will drop into a debugger.
def setup_custom_excepthook(launch_ipdb=False):
  # pylint: disable=global-statement
  global LAUNCH_IPDB

  # If something already patched excepthook, let it win.
  if sys.excepthook == sys.__excepthook__:
    # print ('Using custom excepthook.')
    sys.excepthook = custom_excepthook
  else:
    # print ('Not using custom excepthook.')
    pass

  LAUNCH_IPDB = launch_ipdb


def custom_excepthook(_type, value, tb):
  # print ('Launched custom excepthook.')
  if (hasattr(sys, 'ps1') or
    not sys.stderr.isatty() or
    not sys.stdin.isatty()):
    # Ok, stdin or stderr is redirected, just do the normal thing
    original_hook(_type, value, tb)

    if PRINT_EXCEPTION_LOCALS:
      print_exception_frame_locals(tb)

  else:
    # A terminal is attached and stderr is not redirected, we can debug
    import ipdb

    colorizer = Colorizer('default', False)
    colorizer.colorize_exception_traceback(value, tb)

    if PRINT_EXCEPTION_LOCALS:
      print
      print_exception_frame_locals(tb)

    if LAUNCH_IPDB:
      ipdb.pm()

    # traceback.print_stack()



# Better logging and debugging during development
def print_exception_frame_locals(tb, skip_output=False):
  output = ''
  # Get to the frame where the exception occurred
  while tb.tb_next:
    tb = tb.tb_next

  # import ipdb; ipdb.set_trace()
  output += '------- Locals (capped at 2KB) ----------\n'
  output += pprint.pformat(tb.tb_frame.f_locals)[:2048]
  # output += '\nGlobals:' + pprint.pformat(tb.tb_frame.f_globals)
  output += '\n------- end Locals ----------\n'

  if skip_output:
    print(output)

  return output


# Print local variables from the frame in which the exception occurred.
def get_exception_frame_locals():
  retVal = {}

  if sys.exc_info():
    trace = sys.exc_info()[2]
    print (trace)
    # import ipdb; ipdb.set_trace()
    while trace.tb_next:
      trace = trace.tb_next
    retVal = trace.tb_frame.f_locals

  return retVal

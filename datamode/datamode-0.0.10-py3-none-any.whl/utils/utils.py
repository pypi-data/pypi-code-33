import sys, os, os.path, hashlib, inspect, pprint, json
import numpy as np
import pandas as pd

from .colorizer import Colorizer
from .exceptionutils import print_exception_frame_locals

###
### Utility functions for anywhere in the codebase.
###

import logging

# Dates
DATE_FMT = "%Y-%m-%d"
SHORT_DATE_FMT = "%Y-%m-%d"
DT_FORMAT_DATEONLY = '%-m/%-d/%Y'

# Datetimes
DATETIME_FMT = "%Y-%m-%d %H:%M:%S"

### Logging

# The new way to get the right logger.
# Can't put it in logutils.py because of dependency.
# from utils import get_logger; log = get_logger(__name__)

# NOTE: Cannot do this within this file because of circular dependencies: (!)
# log = get_logger(__name__)
def get_logger(current_context):
  return logging.getLogger(f'{current_context}')


def log_exception_with_context(_log, e, message, print_locals=True):
  try:
    colorizer = Colorizer('default', False, return_content=True)

    output = message + '\n\n'
    output += f'Exception: {e.__class__.__name__}\n'
    output += colorizer.colorize_exception_traceback(e, e.__traceback__)

    if print_locals:
      output += print_exception_frame_locals(e.__traceback__, skip_output=True)

    _log.error(output)

  except Exception as ex:
    msg = f'Further exception in log_exception_with_context: {str(ex)}'
    _log.error(msg)
    print (msg)
    raise ex


def log_error_with_context(_log, message):
  # Print the current stack in color
  colorizer = Colorizer('default', False)
  colorizer.print_current_stack(omit_frames=2)

  locals_str = get_callers_locals()
  _log.error(f'{message}\nLocals:\n{locals_str}')



###
### Misc utilities
###

# Useful in the interactive prompt. Adds classname to unicode output.
class ReprBase():
  def __repr__(self):
    return '<%s: %s>' % (self.__class__.__name__, self.__unicode__())


BLOCK_SIZE = 2**20  # 1MB

# https://stackoverflow.com/questions/1131220/get-md5-hash-of-big-files-in-python
def get_sha1_hash_from_buffer(f, block_size=BLOCK_SIZE):
  sha1 = hashlib.sha1()
  while True:
    data = f.read(block_size)
    if not data:
      break
    sha1.update(data)
  return sha1.hexdigest()


def get_hexhash_from_int(hashtype, _int):
  if type(_int) != int:
    raise Exception('get_hexhash_from_int: input must be of type int')

  if hashtype == 'md5':
    return hashlib.md5(str(_int).encode('ascii')).hexdigest()
  elif hashtype == 'sha1':
    return hashlib.sha1(str(_int).encode('ascii')).hexdigest()
  else:
    raise Exception('get_hexhash_from_int: hashtype not known')


###
### File utilities
###
def ensure_dir(directory):
  if not os.path.exists(directory):
    os.makedirs(directory)


def list_files_in_dir(directory):
  return [f for f in os.listdir(directory) if os.path.isfile(os.path.join(directory, f))]


###
### Logging utils
###

def get_callers_locals():
  """Print the local variables in the caller's caller's frame."""
  frame = inspect.currentframe()
  try:
    return pprint.pformat(frame.f_back.f_back.f_locals)
  finally:
    del frame



###
### Json Utils
###
class DatamodeJsonEncoder(json.JSONEncoder):
  # pylint: disable=arguments-differ
  def default(self, obj):
    if isinstance(obj, pd.Timestamp):
      return obj.isoformat()

    if isinstance(obj, np.int64):
      return str(obj)

    return json.JSONEncoder.default(self, obj)


###
### Introspection
###
# Takes a string with fully qualified class name, e.g. 'some.module.MyClass.my_member_function'
# and returns the class and the function as objects.
def get_class_and_fn_from_str(input_str):
  fq_cls_str, fn_str = input_str.rsplit('.', maxsplit=1)
  _cls = fq_str_to_class(fq_cls_str)
  fn = getattr(_cls, fn_str)
  return _cls, fn


# Modified from https://stackoverflow.com/questions/1176136/convert-string-to-python-class-object
# Expects a fully qualfied string.
def fq_str_to_class(input_str):
  fully_qualified_module_str, _cls_str = input_str.rsplit('.', maxsplit=1)
  try:
    identifier = getattr(sys.modules[fully_qualified_module_str], _cls_str)
  except AttributeError:
    raise NameError("%s doesn't exist." % input_str)

  if inspect.isclass(object):
    return identifier
  raise TypeError("%s is not a class." % input_str)


DONT_YOU_WANT_TO_EXPRESS_YOURSELF = '''
Joanna:
You know what, Stan, if you want me to wear 37 pieces of flair, like your pretty boy over there Bryan, why don't you make the minimum 37 pieces of flair?

Stan:
Well, I thought I remembered you saying that you wanted to express yourself.

Joanna:
You know what, I do want to express myself, okay. And I don't need 37 pieces of flair to do it.'''

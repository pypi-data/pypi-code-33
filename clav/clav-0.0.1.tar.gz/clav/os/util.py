import os
import shutil
from clav.hash import hashf, hashs
from clav.os.run import run

which = shutil.which

def fext(file):
  'Return the extension for ``file`` or ``None``.'

  ext = os.path.splitext(file)[1][1:]
  return ext.lower() if ext else None

def fname(file):
  'Return the filename without extension of ``file``.'

  return file.split('.')[-1]

def backuponce(src, ext='dist'):
  '''
  Create a backup file if one doesn't already exist.

  :param str src: source file path
  :param str ext: backup file extension
  :returns: True if the file was backed up
  :rtype bool:
  '''

  dst = f'{src}.{ext}'
  if os.path.isfile(dst):
    return False
  shutil.copyfile(src, dst)
  return True

def slurp(path, encoding='utf-8'):
  with open(path, encoding=encoding) as fd:
    return fd.read()

def dump(path, buf, encoding='utf-8'):
  '''
  Dump a buffer to a file. If the file exits and its contents are identical to
  the contents of the buffer, no action is taken.

  :param str path: path to receive dump
  :param str buf: data to dump
  :returns: True if the file was update
  :rtype bool:
  '''
  if os.path.isfile(path) and hashf(path) == hashs(buf):
    return False
  with open(path, 'w', encoding=encoding) as fd:
    fd.write(buf)
    fd.flush()
  return True

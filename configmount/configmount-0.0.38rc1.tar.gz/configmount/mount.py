#!/usr/bin/python
# -*- coding: utf-8 -*-
'''
config/mount.py - Directive for mounting data to file system with Python-LLFUSE.

This file system stores all data in memory. It is compatible with Python 3.x.

Copyright © 2017 Dominik Kummer <Arkades.org>

Permission is hereby granted, free of charge, to any person obtaining a copy of
this software and associated documentation files (the "Software"), to deal in
the Software without restriction, including without limitation the rights to
use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of
the Software, and to permit persons to whom the Software is furnished to do so.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS
FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR
COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER
IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN
CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
'''

import os
import sys
import errno

import argparse
import llfuse

try:
    import faulthandler
except ImportError:
    pass
else:
    faulthandler.enable()


# For Python 2 + 3 compatibility
if sys.version_info[0] == 2:
    def next(it):
        return it.next()
else:
    buffer = memoryview
    

class PathType(object):
  def __init__(self, exists=True, type='file', dash_ok=True):
    '''exists:
        True: a path that does exist
        False: a path that does not exist, in a valid parent directory
        None: don't care
      type: file, dir, symlink, None, or a function returning True for valid paths
        None: don't care
      dash_ok: whether to allow "-" as stdin/stdout'''

    assert exists in (True, False, None)
    assert type in ('file','dir','symlink',None) or hasattr(type,'__call__')

    self._exists = exists
    self._type = type
    self._dash_ok = dash_ok

  def __call__(self, string):
    if string=='-':
      # the special argument "-" means sys.std{in,out}
      if self._type == 'dir':
        raise err('standard input/output (-) not allowed as directory path')
      elif self._type == 'symlink':
        raise err('standard input/output (-) not allowed as symlink path')
      elif not self._dash_ok:
        raise err('standard input/output (-) not allowed')
    else:
      e = os.path.exists(string)
      if self._exists==True:
        if not e:
          raise err("path does not exist: '%s'" % string)

        if self._type is None:
          pass
        elif self._type=='file':
          if not os.path.isfile(string):
            raise err("path is not a file: '%s'" % string)
        elif self._type=='symlink':
          if not os.path.symlink(string):
            raise err("path is not a symlink: '%s'" % string)
        elif self._type=='dir':
          if not os.path.isdir(string):
            raise err("path is not a directory: '%s'" % string)
        elif not self._type(string):
          raise err("path not valid: '%s'" % string)
      else:
        if self._exists==False and e:
          raise err("path exists: '%s'" % string)

        p = os.path.dirname(os.path.normpath(string)) or '.'
        if not os.path.isdir(p):
          raise err("parent path is not a directory: '%s'" % p)
        elif not os.path.exists(p):
          raise err("parent directory does not exist: '%s'" % p)

    return string

def main(*args, **kwargs):
  import operations
  
  operations = operations.Config(**kwargs)
  
  fuse_options = set(llfuse.default_options)
  fuse_options.add('fsname=tmpfs')
  fuse_options.discard('default_permissions')
  #fuse_options.add('allow_other')
  if kwargs.get('debug_fuse', False):
    fuse_options.add('debug')
  llfuse.init(operations, kwargs.get('mountpoint'), fuse_options)
  try:
    # Store the Fork PID
    pid = os.fork()
    if pid > 0:
      os._exit(0)
  except OSError as error:
    print('Unable to fork. Error: %d (%s)' % (error.errno, error.strerror))
    os._exit(1)
    
  try:
    llfuse.main(workers=1)
  except:
    llfuse.close(unmount=False)
    raise
  llfuse.close()

HELP = "Mount configuration files as virtual filesystem."

def getargs(parser):
  parser.add_argument('mountpoint', type=str,
                      help='Path to mount the file system to')
  parser.add_argument('-f', '--files', dest='files',
                      metavar='SOURCE', nargs="+",
                      type=argparse.FileType('r'),
                      help='Source configuration file[s]')
  parser.add_argument('-d', '--dirs', dest='dirs',
                      metavar='SOURCEDIR', nargs="+",
                      type=PathType(True, 'dir'), 
                      help='Source configuration directory')
  parser.add_argument('--root', default=None, dest='root',
                      help='Root directory to mount files from')
  parser.add_argument('--debug-fuse', action='store_true', default=False,
                      help='Enable FUSE debugging output')
  
if __name__ == "__main__":
  parser = argparse.ArgumentParser(prog=os.path.basename(os.path.splitext(__file__)[0]), description=HELP)
  getargs(parser)
  if len(sys.argv) < 2:
    parser.print_usage()
    sys.exit(1)
  else:
    Args = parser.parse_args(sys.argv[1:])
    main(**vars(Args))


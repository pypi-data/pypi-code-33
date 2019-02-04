#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""A set of utilities and library functions to handle keypoint annotations."""

import os
import six
import json
import fnmatch


def uniq(seq, idfun=None):
   '''Order preserving uniq for lists

   See: https://www.peterbe.com/plog/uniqifiers-benchmark
   '''

   if idfun is None:
       def idfun(x): return x
   seen = {}
   result = []
   for item in seq:
       marker = idfun(item)
       if marker in seen: continue
       seen[marker] = 1
       result.append(item)
   return result


def save(data, fp, backup=False):
  """Saves a given data set to a file


  Parameters:

  data (list): A list of lists, each containing points in the format ``(y,x)``

  fp (file, str): The name of a file, with full path, to be used for recording
    the data or an already opened file-like object, that accepts the "write()"
    call.

  backup (boolean, Optional): If set, backs-up a possibly existing file path
    before overriding it. Note this is not valid in case 'fp' above points to
    an opened file.

  """

  if isinstance(fp, six.string_types):

    if backup and os.path.exists(fp):
      bname = fp + '~'
      if os.path.exists(bname): os.unlink(bname)
      os.rename(fp, bname)

    fp = open(fp, 'w')

  json.dump(data, fp, indent=2)


def load(fp):
  """Loads a given data set from file


  Parameters:

    fp (str, :py:obj:`object`): The name of a file, with full path, to be used
      for reading the data or an already opened file-like object, that accepts
      the "read()" call.


  Returns:

    list: A list of lists, each containing points in the format ``(y,x)``

  """

  if isinstance(fp, six.string_types):
    fp = open(fp, 'r')

  return json.load(fp)


def find(basedir, name):
  """Finds all files on basedir that match the given name

  Parameters:

    basedir (str): Base path to search for files
    name (str): A string, maybe a glob, with an expression to search for

  Returns:

    list: List of paths that match the given name glob

  """

  retval = []
  for root, dirs, files in os.walk(basedir):
    matched = fnmatch.filter(files, name)
    retval += [os.path.join(root, k) for k in matched]
  retval.sort()
  return retval

#!/usr/bin/python
# -*- coding: utf-8 -*-
'''
config/data.py - FUSE Data class holding yaml and augeas cache to file system with Python-LLFUSE.

This file system stores all data in configuration directory. It is compatible with both Python 3.x.

Copyright © 2019 Dominik Kummer <admin@arkades.org>

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

import os, re, stat
import fnmatch, dpath, errno
import augeas, json, yaml

from lockfile import LockFile
from llfuse import FUSEError


class AugeasError(Exception):
    def __init__(self, aug):
        self.message = None
        self.data = {}
        #aug.dump('/')
        for ep in aug.match('/augeas//error'):
            self.message = aug.get(ep + '/message')
            for p in aug.match(ep + '/*'):
                self.data[p.split('/')[-1]] = aug.get(p)

    def __str__(self):
        return self.message


def natural_rsort(l): 
    convert = lambda text: int(text) if text.isdigit() else text.lower() 
    alphanum_key = lambda key: [ convert(c) for c in re.split('([0-9]+)', key) ] 
    return sorted(l, key = alphanum_key, reverse=True)

def yaml_path_replace(match):
  return "/" + str(int(match.group('index'))-1) + match.group('delim')

def ryaml_path_replace(match):
  return "[" + str(int(match.group('index'))+1) + "]" + match.group('delim')

yaml_path_pattern = re.compile(r'\[(?P<index>[0-9]+)\](?P<delim>/|$)')
ryaml_path_pattern = re.compile(r'/(?P<index>[0-9]+)(?P<delim>/|$)')
index_func_pattern = re.compile("(?P<name>^[^\[]+)\[(?P<index>[^\]]+)\]$")
index_pattern = re.compile("^\[(?P<index>[0-9]+)\]$")
interface_pattern = re.compile("^.*/#interface$")


#TODO: cleanup and single out yaml functionality into a separate class
# to inherit from.

class Proxy(augeas.Augeas):
  """
  A smarter and faster wrapper around :class:`augeas.Augeas`.augeas

  For faster startup, no modules and lenses are preloaded::

    aug = Augeas(modules=[{
      'name': 'Interfaces',  # module name
      'lens': 'Interfaces.lns',  # lens name
      'incl': [  # included files list
        self.path,
        self.path + '.d/*',
      ]
    }])

  Don't forget to call :func:`.load()` afterwards.
  """
  
  files = []
  dirs = []
  root = '/'
  loadpath = None
  
  def __init__(self, *args, **kwargs):
    self.files = kwargs.get('files') or self.files
    self.dirs = kwargs.get('dirs') or self.dirs
    self.root = kwargs.get('root') or self.root
    self.loadpath = kwargs.get('loadpath') or self.loadpath
    
    if not self.files and not self.dirs:
      raise ValueError("files/dirs must be a list of files/directories.")
    self.fileroot = '/files'
    self.augfiles = []
    self.includes = {}
    self.configtypes = []
    self.yamlfiles = []
    self.yamldata = {}
    self.yamlmap = {}
    self.recent = {}
    self.recent_path = []
    self.recent_value = []
    self.includes_extra = {}
    self.includes_extra['Iptables'] = '/etc/iptables/*'
    
    self.confglobs = ['*.conf', '*.config', '*.cf', '*.cfg', '*.ini', '*.txt', '*rc', '*.yaml', '*.yml', '*.json']
    if not os.path.isdir(self.root):
      self.root = '/'
      
    augeas.Augeas.__init__(self, root=self.root, loadpath=self.loadpath, flags=augeas.Augeas.NO_LOAD)
    
    augeas_rm = []
    includes = []
    in_class = augeas.Augeas.match(self, '/augeas/load/*/incl')
    confglobs = self.confglobs
    for incl in in_class:
      glob = augeas.Augeas.get(self, incl)
      for i, g in enumerate(confglobs):
        if fnmatch.fnmatch(glob, g):
          break
        elif i+1 == len(confglobs):
          self.confglobs.append(glob)
      lens = os.path.dirname(incl) + '/lens'
      self.includes[glob] = (incl, lens, augeas.Augeas.get(self, lens))
    if self.files:
      for file in self.files:
        if not os.path.isfile(file.name)\
          or file.name in self.augfiles: continue
        for glob in self.includes:
          incl = self.includes[glob][0]
          if fnmatch.fnmatch(file.name, glob):
            if file.name not in self.augfiles:
              self.augfiles.append(file.name)
            if incl not in includes:
              includes.append(incl)
            if incl in augeas_rm:
              augeas_rm.remove(incl)
            break
          elif not file.name in self.augfiles \
            and incl not in augeas_rm \
            and incl not in includes:
              augeas_rm.append(incl)
        if file.name not in self.augfiles:
          self.yamlfiles.append(file.name)
    else:
      for glob in self.includes:
        incl = self.includes[glob][0]
        if incl not in augeas_rm \
          and incl not in includes:
            augeas_rm.append(incl)
      
    for dir in self.dirs:
      self.set(dir, {})
    for rm in natural_rsort(augeas_rm):
      augeas.Augeas.remove(self, rm)
    for rm in augeas.Augeas.match(self, '/augeas/load/*[count(./incl) = 0]'):
      augeas.Augeas.remove(self, rm)
    for key, ie in self.includes_extra.items():
      augeas.Augeas.set(self, '/augeas/load/' + key + '/incl[last()+1]', ie)
    self.load()
  
  def load(self, path=None):
    if path \
      and os.path.isfile(path):
      for glob in self.includes:
        if fnmatch.fnmatch(path, glob):
          lenspath = self.includes[glob][1]
          lens = self.includes[glob][2]
          incl = os.path.dirname(lenspath) + '/incl[last()+1]'
          augeas.Augeas.set(self, lenspath, lens)
          augeas.Augeas.set(self, incl, glob)
          augeas.Augeas.load(self)
          if not path in self.augfiles:
            self.augfiles.append(path)
          return True
      try:
        with open(path, 'r') as f:
          data = yaml.load(f)
          if data is None: data = {}
          dpath.util.new(self.yamldata, path, data)
          if not path in self.yamlfiles:
            self.yamlfiles.append(path)
          return True
      except:
        return False
    elif path is None:
      try:
        augeas.Augeas.load(self)
        for y in self.yamlfiles:
          with open(y, 'r') as f:
            data = yaml.load(f)
            dpath.util.new(self.yamldata, y, data)
        return True
      except:
        return False
  
  def unload(self, path):
    if path in self.augfiles:
      try:
        augeas.Augeas.remove(path)
      except:
        pass
      for rm in augeas.Augeas.match(self, "/augeas/load/*/incl[. = '"+path+"']"):
        augeas.Augeas.remove(rm)
      self.augfiles.remove(path)
      return True
    elif path in self.yamlfiles:
      try:
        dpath.util.delete(self.yamldata, path)
      except:
        pass
      self.yamlfiles.remove(path)
      return True
    return False
    
    
  def save(self, path=None):
    log.info('save')
    if path \
      and os.path.isfile(path):
      for glob in self.includes:
        if fnmatch.fnmatch(path, glob):
          augeas.Augeas.save(self)
          return True
      try:
        if path in self.yamlfiles:
          data = dpath.util.get(self.yamldata, path)
          with open(path, 'w') as f:
            yaml.dump(data, f, default_flow_style=False)
            return True
      except:
        self.raise_error()
    elif path is None:
      try:
        augeas.Augeas.save(self)
        for y in self.yamlfiles:
          data = dpath.util.get(self.yamldata, y)
          with open(y, 'w') as f:
            yaml.dump(data, f, default_flow_style=False)
        return True
      except IOError:
        self.raise_error()
        
    
  def stat(self, path=None):
    try:
      if path:
        if os.path.exists(path) \
          or path in self.augfiles \
          or path in self.yamlfiles:
          return os.stat(path)
        for a in self.augfiles:
          if path.startswith(a) or fnmatch.fnmatch(a, path):
            return os.stat(a)
        for y in self.yamlfiles:
          if path.startswith(y) or fnmatch.fnmatch(y, path):
            return os.stat(y)
    except:
      pass
    return os.stat(os.path.expanduser('~'))
  
  def _isconfigure(self, path):
    for g in self.confglobs:
      if fnmatch.fnmatch(path, g):
        return True
    return False
  
  def _file_path(self, path):
    for a in self.augfiles:
      if path.startswith(a):
        return a
    for y in self.yamlfiles:
      if path.startswith(y):
        return y
    return path
    
  def _yaml_path(self, path):
    base = os.path.basename(path)
    match = index_func_pattern.search(base)
    if match and match.group('index'):
      base = match.group('name')
      if os.path.dirname(path) != "/":
        basepath = os.path.dirname(path) + '/' + base
      else:
        basepath = os.path.dirname(path) + base
      func = str(match.group('index'))
      if "last()" in func:
        try:
          v = dpath.util.get(self.yamldata, yaml_path_pattern.sub(yaml_path_replace, basepath))
          if isinstance(v, list):
            last = len(v)
          else:
            last = 1
        except:
          last = 1
        func = func.replace('last()', str(last))
        index = eval(func)
        path = basepath + '[' + str(index) + ']'
    else:
      if os.path.dirname(path) != "/":
        basepath = os.path.dirname(path) + '/' + base
      else:
        basepath = os.path.dirname(path) + base
    return yaml_path_pattern.sub(yaml_path_replace, path)
  
  def _ryaml_path(self, path):
    return ryaml_path_pattern.sub(ryaml_path_replace, path)

  def _aug_path(self, path):
    return self.fileroot + path
  
  def _raug_path(self, path):
    return path.split(self.fileroot, 1).pop()

  def _rel_path(self, path):
    return path.split(self.fileroot, 1).pop()

  def _get_recent(self, path, value=None, default="[last()]"):
    dirname = os.path.dirname(path)
    basename = os.path.basename(path)
    basedir = path.replace('[@]', '')
    if basename.endswith('[@]') \
      and basedir in self.recent:
        path = self.recent[basedir]
    elif default and basename.endswith('[@]'):
      path = path.replace('[@]', default)
    
    if path in self.recent_path \
      and 'last()' not in path \
      and value is None:
      i = self.recent_path.index(path)
      value = self.recent_value[i]
    
    return path, value
  
  
  def _set_recent(self, path, value=None):
    if path is None: return None, None
    base = os.path.basename(path)
    match = index_func_pattern.search(base)
    if match and match.group('name'):
      base = match.group('name')
    basedir = os.path.dirname(path) + '/' + base
    self.recent[basedir] = path
    self.recent_path.append(path)
    self.recent_value.append(value)
    if len(self.recent_path) > 4:
      del self.recent_path[0]
      del self.recent_value[0]
    return path, value
      

  def match(self, path):
    if interface_pattern.match(os.path.basename(path)):
      return [path]
    path, value = self._get_recent(path)
    augpath = self._aug_path(path)
    augbase = os.path.basename(os.path.dirname(augpath))
    result = []
    
    for m in augeas.Augeas.match(self, augpath):
      name = os.path.basename(m)
      indexbase = os.path.basename(os.path.dirname(m))
      index = indexbase.split(augbase, 1).pop()
      if index_pattern.match(index):
        break
      else:
        realpath = self._rel_path(m)
        if realpath not in self.augfiles \
          and os.path.isfile(realpath):
          self.augfiles.append(realpath)
        result.append(realpath)
    try:
      yamlpath = self._yaml_path(path)
      for m in dpath.util.search(self.yamldata, yamlpath, yielded=True):
        p = '/' + m[0]
        v = m[1]
        if isinstance(v, list):
          for i, e in enumerate(v):
            r = p + '/' + str(i)
            r = self._ryaml_path(r)
            if r not in result:
              result.append(r)
        else:
          b = os.path.basename(p)
          d = os.path.dirname(p)
          if b != p and d != '/':
            r = self._ryaml_path(d) + '/' + b
          else:
            r = self._ryaml_path(p)
          if r not in result:
            result.append(r)
    except:
      pass
    return result
  
  
  def set(self, path, value):
    log.debug('set %s : %s' % (path, value))
    if interface_pattern.match(os.path.basename(path)):
      if value.rstrip() == 'save':
        self.save(os.path.dirname(path))
      else:
        raise(FUSEError(errno.EACCES))
      return self._set_recent(path, value)
    for a in self.augfiles:
      if a == path:
        with open(path, "w") as outfile:
          outfile.write(value + '\n')
        self.load(path)
      elif re.compile(a + "\[[^\]]+\]$").search(path):
        raise(FUSEError(errno.EACCES))
      elif path.startswith(a) or fnmatch.fnmatch(a, path):
        augpath = self._aug_path(path)
        try:
          augeas.Augeas.set(self, augpath, value)
        except:
          augeas.Augeas.set(self, augpath + '/temp', None)
          augeas.Augeas.remove(self, augpath.replace("[last()+1]", "[last()]") + '/temp')
        if "[last()+1]" in augpath:
          path = self._raug_path(augeas.Augeas.match(self, augpath.replace("[last()+1]", "[last()]"))[0])
          return self._set_recent(path, value)
        else:
          path = self._raug_path(augpath)
          return self._set_recent(path, value)
    
    for y in self.yamlfiles:
      if os.path.dirname(path) == y \
        and sum(1 for _ in dpath.util.search(self.yamldata, os.path.dirname(path) + '/*', yielded=True)) >= 1:
        raise(FUSEError(errno.EACCES))
      log.debug('%s : %s' % (y, path))
      if y == path:
        with open(path, "w") as outfile:
          outfile.write(value + '\n')
        self.load(path)
      elif re.compile(y + "\[[^\]]+\]$").search(path):
        raise(FUSEError(errno.EACCES))
      elif path.startswith(y) or fnmatch.fnmatch(y, path):
        yamlpath = self._yaml_path(path)
        m = re.search(r'/(\d+)$', yamlpath)
        if m is not None:
          index = int(m.group(1))
          test = os.path.dirname(yamlpath)
          try:
            v = dpath.util.get(self.yamldata, test)
            if not isinstance(v, list):
              if index == 0:
                yamlpath = test
              elif index > 0:
                dpath.util.set(self.yamldata, test, [v])
          except:
            dpath.util.new(self.yamldata, test, [])
        try:
          dpath.util.get(self.yamldata, yamlpath)
          dpath.util.set(self.yamldata, yamlpath, value)
        except:
          dpath.util.new(self.yamldata, yamlpath, value)
        
        path = self._ryaml_path(yamlpath)
        return self._set_recent(path, value)
    
    try:
      if isinstance(value, dict):
        if self._isconfigure(path):
          with open(path, "w") as outfile:
            outfile.write('\n')
            outfile.close()
          if self.load(path):
            path, value = self.get(path)
        else:
          if not os.path.exists(path): os.makedirs(path, exist_ok=True)
          try:
            dpath.util.get(self.yamldata, path)
            dpath.util.set(self.yamldata, path, value)
          except:
            dpath.util.new(self.yamldata, path, value)
      elif value == '{}':
        open(path, 'a').close()
        if self.load(path):
          path, value = self.get(path)
      elif value and isinstance(value, str):
        with open(path, "w") as outfile:
          outfile.write(value + '\n')
          outfile.close()
        if self.load(path):
          path, value = self.get(path)
      else:
        open(path, 'a').close()
        if os.path.getsize(path) > 0:
          if self.load(path):
            path, value = self.get(path)
        else:
          try:
            dpath.util.get(self.yamldata, path)
            dpath.util.set(self.yamldata, path, value)
          except:
            dpath.util.new(self.yamldata, path, value)
    except:
      raise(FUSEError(errno.EACCES))
    
    return path, value
  
  
  def get(self, path, strict=False, boolean=False):
    if interface_pattern.match(os.path.basename(path)):
      return path, "Interface to write instructions [save]"
    if strict is False:
      path, value = self._get_recent(path)
      if value is not None:
        return path, value
    if isinstance(path, str):
      if path not in self.augfiles \
        and path not in self.yamlfiles \
        and os.path.isdir(path) \
        and os.access(path, os.R_OK):
          try:
            value = next(dpath.util.search(self.yamldata, path, yielded=True), (None, None))[1]
            if value is None:
              path, value = self.set(path, {})
          except:
            value = {}
      elif path not in self.augfiles \
        and path not in self.yamlfiles \
        and os.path.isfile(path) \
        and os.access(path, os.R_OK):
          if self.load(path):
            path, value = self.get(path)
      else:
        for a in self.augfiles:
          if path.startswith(a) or fnmatch.fnmatch(a, path):
            augpath = self._aug_path(path)
            match = augeas.Augeas.match(self, augpath)
            path = self._raug_path(augpath)
            if len(match) > 0:
              augpath = match[0]
              value = augeas.Augeas.get(self, augpath)
              if value is None:
                value = {}
            elif value is None and os.path.isfile(path):
              value = {}
            else:
              value = None
            break
        for y in self.yamlfiles:
          if path.startswith(y) or fnmatch.fnmatch(y, path):
            yamlpath = self._yaml_path(path)
            for match in dpath.util.search(self.yamldata, yamlpath, yielded=True):
              path = '/' + match[0]
              value = match[1]
              if value is not None and isinstance(value, list):
                path = self._ryaml_path(path)
                if not strict:
                  value = value[0]
              else:
                path = self._ryaml_path(path)
              break
            break
    if value is None:
      path = None
    if boolean is True:
      path, value = self._set_recent(path, value)
      if value is not None:
        return True
      else:
        return False
    else:
      if strict is True:
        return path, value
      else:
        return self._set_recent(path, value)
  
  
  def move(self, path, path_new):
    if interface_pattern.match(os.path.basename(path)):
      raise(FUSEError(errno.EACCES))
    path, value = self._get_recent(path)
    path_new, value_new = self._get_recent(path_new)
    if path == path_new: return
    if os.path.exists(path) \
      and os.access(path, os.W_OK) \
      and os.getuid() == os.stat(path).st_uid:
        try:
          os.rename(path, path_new)
        except:
          raise(FUSEError(errno.ENOENT))
    new_augfiles = []
    for a in self.augfiles:
      if a.startswith(path) and a != path:
        suffix = a.split(path + '/', 1).pop()
        a_new = path_new + '/' + suffix
        augpath = self._aug_path(path + '/' + suffix)
        augpath_new = self._aug_path(path_new + '/' + suffix)
        augeas.Augeas.move(self, augpath, augpath_new)
        new_augfiles.append(a_new)
      elif path.startswith(a) or fnmatch.fnmatch(a, path):
        augpath = self._aug_path(path)
        augpath_new = self._aug_path(path_new)
        augeas.Augeas.move(self, augpath, augpath_new)
        new_augfiles.append(a)
    self.augfiles = new_augfiles
    
    new_yamlfiles = []
    for y in self.yamlfiles:
      if y.startswith(path) and y != path:
        suffix = y.split(path + '/', 1).pop()
        y_new = path_new + '/' + suffix
        yamlpath = self._yaml_path(path + '/' + suffix)
        yamlpath_new = self._yaml_path(path_new + '/' + suffix)
        v = dpath.util.get(self.yamldata, yamlpath)
        if hasattr(v, 'copy'):
          v = v.copy()
        dpath.util.new(self.yamldata, yamlpath_new, v)
        dpath.util.delete(self.yamldata, yamlpath)
        new_yamlfiles.append(y_new)
      elif path.startswith(y) or fnmatch.fnmatch(y, path):
        yamlpath = self._yaml_path(path)
        yamlpath_new = self._yaml_path(path_new)
        v = dpath.util.get(self.yamldata, yamlpath)
        if hasattr(v, 'copy'):
          v = v.copy()
        dpath.util.new(self.yamldata, yamlpath_new, v)
        dpath.util.delete(self.yamldata, yamlpath)
        new_yamlfiles.append(y)
    self.yamlfiles = new_yamlfiles
      
      
  def remove(self, path):
    if interface_pattern.match(os.path.basename(path)):
      raise(FUSEError(errno.EACCES))
    path, dummy = self._get_recent(path)
    if os.path.exists(path) \
      and os.access(path, os.W_OK) \
      and os.getuid() == os.stat(path).st_uid:
        if os.path.isdir(path) \
          and len(os.listdir(path)) == 0:
          os.rmdir(path)
        else:
          os.remove(path)
    for a in self.augfiles:
      if path.startswith(a) or fnmatch.fnmatch(a, path):
        augpath = self._aug_path(path)
        augeas.Augeas.remove(self, augpath)
        self.unload(path)
    for y in self.yamlfiles:
      if path.startswith(y) or fnmatch.fnmatch(y, path):
        yamlpath = self._yaml_path(path)
        dpath.util.delete(self.yamldata, yamlpath)
        self.unload(path)
  
  
  def insert(self, path, value, before=0):
    if interface_pattern.match(os.path.basename(path)):
      raise(FUSEError(errno.EACCES))
    path, value = self._get_recent(path, value)
    for a in self.augfiles:
      if path.startswith(a) or fnmatch.fnmatch(a, path):
        augpath = self._aug_path(path)
        augeas.Augeas.insert(self, augpath, value, before)
        return self.get(augpath_new)
    for y in self.yamlfiles:
      if path.startswith(y) or fnmatch.fnmatch(y, path):
        yamlpath = self._yaml_path(path)
        yamlpath_new = self._yaml_path(path_new)
        v = dpath.util.get(self.yamldata, yamlpath)
        if hasattr(v, 'copy'):
          v = v.copy()
        dpath.util.new(self.yamldata, yamlpath_new, v)
        dpath.util.delete(self.yamldata, yamlpath)
        return dpath.util.get(self.yamldata, yamlpath_new)
    
    
  def setd(self, path, value, default=None):
    """
    Sets `path` to `value`, or removes `path` if `value == default`
    """
    if interface_pattern.match(os.path.basename(path)):
      raise(FUSEError(errno.EACCES))
    if value is not None:
      self.set(path, value)
    if value == default:
      self.remove(path)


  def raise_error(self):
    """
    Extracts error information from Augeas tree and raises :exc:`AugeasError`
    """
    raise AugeasError(self)


  def dump(self, path):
    """
    Dumps contents under `path` to stdout.
    """
    for sp in self.match(path + '/*'):
      p, v = self.get(sp)
      


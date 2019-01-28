#!/usr/bin/python
# -*- coding: utf-8 -*-
'''
config/operations.py - FUSE Operation for mounting yaml configuration to file system with Python-LLFUSE.

This file system stores all data in configuration directory. It is compatible with both Python 3.x.

Copyright © 2017 Dominik Kummer <domson.at>

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
import xattr
import re
import datetime
import llfuse
import errno
import stat
import data
from helpers import watchdog
from time import time
from shutil import rmtree
from lockfile import LockFile
from collections import defaultdict
from llfuse import FUSEError


index_name_pattern = re.compile("(?P<name>^[^\[]+)\[(?P<index>[0-9]*)\]$")
name_allowed_pattern = re.compile("(?P<name>^#?[*]|[a-zA-Z0-9_.]+)(\[([0-9]+|@)\])?$")
index_empty_pattern = re.compile("(?P<name>^[^\[]+)\[\]$")
name_hidden_pattern = re.compile("^[.].+$")


class Config(llfuse.Operations):
  '''Filesystem that stores all data in yaml file
  
  There are some flaws that have not been fixed to keep 
  the code easier to understand:

  * atime, mtime and ctime are not updated
  * generation numbers are not supported
  '''

  def __init__(self, *args, **kwargs):
    super(Config, self).__init__()
    self.data = data.Proxy(*args, **kwargs)
    self.wd = watchdog.Watchdog(timeout=5, event=self.save)
    self.inode_count = -1
    self.nodemap = []
    self.lockfiles = {}
    self.root()
    self.CREATED = False
    self.EMPTYLOOKUP = False
    self.inode_open_count = defaultdict(int)
    self.inode_lookup_count = defaultdict(int)
    
  
  def lock(self, file):
    self.lockfiles[file] = LockFile(file)
    self.lockfiles[file].acquire()
    
  def unlock(self, file):
    self.lockfiles[file].release()
    del self.lockfiles[file]
    
  def save(self):
    self.data.save()
    for k, v in self.lockfiles.items():
      self.unlock(file)

  def root(self):
    '''Initialize file system tables'''
    
    # Insert root directory
    now_ns = int(time() * 1e9)
  
    self.nodemap.append({'rowid': len(self.nodemap), 'name': b'..', 'id': llfuse.ROOT_INODE, 'pid': 0, 'path': '/', 'nameindex': 0, 'index': 0, 'target': None, 'xattrs': {}})
    self.inode_count = llfuse.ROOT_INODE
  
  
  def _name_index(self, name_q, inode_p=None):
    if isinstance(name_q, bytes):
      name_q = name_q.decode()
    if inode_p and "[@]" in name_q:
      basedir = self._get_row(lambda node: node.get('id', '') == inode_p)['path']
      path = basedir + '/' + name_q
      path, dummy = self.data._get_recent(path, None)
      if path is None:
        raise(FUSEError(errno.ENOENT))
      name_q = os.path.basename(path)
    
    match = index_name_pattern.search(name_q)
    if match and match.group('index'):
      return match.group('name').encode('utf8'), int(match.group('index'))
    else:
      return name_q.encode('utf8'), 1
    
  def _name_subst(self, name, default='0'):
    if isinstance(name, bytes):
      name = name.decode()
    match = index_name_pattern.search(name)
    if match and match.group('index'):
      name = match.group('name') + '[' + match.group('index') + ']'
      return name.encode('utf8')
    elif match and match.group('name'):
      name = match.group('name') + '[' + default + ']'
      return name.encode('utf8')
    else:
      return name.encode('utf8')
    
  def _row_path(self, row, force=False):
    try:
      p, v = self.data.get(row['path'], strict=True)
      if not isinstance(v, list) \
        and not isinstance(v, dict):
        try:
          temp = self.data.match(row['path'])
          if len(temp) > 1:
            v = temp
        except:
          pass
    except:
      v = None
    if isinstance(v, list):
      length = len(v)
    else:
      length = 1
    
    if ( force and not os.path.exists(row['path']) and length > 1) \
      or isinstance(v, list):
      return row['path'] + '[' + str(row['index']) + ']'
    else:
      return row['path']
    
  def _get_row(self, f):
    for i, node in enumerate(self.nodemap):
      node["rowid"] = i
      if f(node):
        return node
    raise NoSuchRowError()
  
  def _get_rows(self, f):
    result = []
    for i, node in enumerate(self.nodemap):
      node["rowid"] = i
      if f(node):
        result.append(node)
    return result
  
  
  def _load_row(self, inode, name=None, path=None):
    if isinstance(name, bytes): name = name.decode()
    if path is None:
      path = self._row_path(self._get_row(lambda node: node.get('id', '') == inode))
    if name:
      name = self._name_subst(name, 'last()')
      if path == '/':
        path = path + name.decode()
      else:
        path = path + '/' + name.decode()
    else:
      name = self._name_subst(os.path.basename(path), 'last()')
      path = os.path.dirname(path)
      if path == '/':
        path = path + name.decode()
      else:
        path = path + '/' + name.decode()
    if name.decode().startswith('#comment'): raise NoSuchRowError()
    path, value = self.data.get(path)
      
    if path is None:
      raise NoSuchRowError()
    
    basename = os.path.basename(path)
    name, index = self._name_index(basename)
    
    try:
      row = self._get_row(lambda node: node.get('pid', '') == inode and node.get('name', '') == name and node.get('index', '') == index)
      row['nameindex'] = index
      return row
    except:
      path = os.path.dirname(path)
      if path == '/':
        path = path + name.decode()
      else:
        path = path + '/' + name.decode()
      self.inode_count += 1
      log.info('name: %s, ino: %d, path: %s', name, index, path)
      self.nodemap.append({'rowid': len(self.nodemap), 'name': name, 'id': self.inode_count, 'pid': inode, 'path': path, 'nameindex': index, 'index': index, 'target': None, 'xattrs': {}})

      if os.path.isdir(path) and self.data.get(path, boolean=True) is False:
        self.data.set(path, value)
      return self.nodemap[-1]

  
  def _load_rows(self, inode, off=-1):
    result = []
    try:
      path = self._row_path(self._get_row(lambda node: node.get('id', '') == inode))
      if path == '/': path = ''
      log.info('%s', path + '/*')
      children = self.data.match(path + '/*')
      for path in children:
        name = None
        try:
          if isinstance(path, tuple):
            name = path[0]
            path = path[1]
          if not isinstance(path, str):
            return result
          row = self._load_row(inode, name, path)
          if row['id'] <= off:
            continue
          result.append(row)
        except:
          pass
    except:
      pass
    return result


  def del_rows(self, f):
    log.info('ino: %d', f)
    for i, node in enumerate(reversed(self.nodemap)):
      node["rowid"] = i
      if f(node):
        self.del_rows(lambda node: node.get('pid', '') == node['id'])
        self.nodemap.remove(node)
  
  def forget(self, inode_list):
    log.info('ino: %s', inode_list)
    for touple in inode_list:
      inode = touple[0]
      nlookup = touple[1]
      self.inode_lookup_count[inode] -= nlookup
      if self.inode_lookup_count[inode] <= 0:
        self.inode_lookup_count[inode] = 0
        self.del_rows(lambda node: node.get('id', '') == inode)
    
  def flush(self, fh):
    log.info('ino: %d', fh)
    
  def destroy(self):
    inode_list = []
    for inode in self.inode_lookup_count:
      if self.inode_lookup_count[inode] > 0:
        inode_list.append((inode, self.inode_lookup_count[inode]))
    if inode_list:
      self.forget(inode_list)

  def lookup(self, inode_p, name_q, ctx=None):
    if ((not self.CREATED and \
      not name_allowed_pattern.search(name_q.decode())) \
      or index_empty_pattern.search(name_q.decode()) \
      or name_hidden_pattern.search(name_q.decode())):
      if index_empty_pattern.search(name_q.decode()):
        self.EMPTYLOOKUP = True
      log.info('blocked: ino: %d name: %s', inode_p, name_q)
      entry = llfuse.EntryAttributes()
      entry.generation = 0
      entry.st_ino = 0
      entry.entry_timeout = 0
      entry.attr_timeout = 0
      return entry
    log.info('ino: %d name: %s', inode_p, name_q)
    self.CREATED = False
    name, index = self._name_index(name_q, inode_p)
    if name == '.':
      row = self._get_row(lambda node: node.get('id', '') == inode_p)
      inode = row['id']
    elif name == '..':
      row = self._get_row(lambda node: node.get('pid', '') == inode_p)
      inode = row['id']
    else:
      try:
        row = self._get_row(lambda node: node.get('pid', '') == inode_p and node.get('nameindex', '') == index and node.get('name', '') == name)
        inode = row['id']
      except NoSuchRowError:
        try:
          row = self._load_row(inode_p, name_q)
          inode = row['id']
        except NoSuchRowError:
          raise(FUSEError(errno.ENOENT))
    self.inode_lookup_count[inode] += 1
    return self.getattr(inode, ctx, row, 0)


  def getattr(self, inode, ctx=None, row=None, timeout=100):
    if row is not None and isinstance(row, dict):
      inode = row['id']
      path = self._row_path(row)
      path, value = self.data.get(path)
    else:
      row = self._get_row(lambda node: node.get('id', '') == inode)
      path = self._row_path(row)
      path, value = self.data.get(path)
      
    if self.EMPTYLOOKUP:
      timeout = 0
      self.EMPTYLOOKUP = False
    datastat = self.data.stat(path)
    
    entry = llfuse.EntryAttributes()
    entry.st_ino = inode
    entry.st_atime_ns = datastat.st_atime_ns
    entry.st_mtime_ns = datastat.st_mtime_ns
    entry.st_ctime_ns = datastat.st_ctime_ns
    entry.generation = 0
    entry.entry_timeout = timeout
    entry.attr_timeout = timeout
    entry.st_blksize = 512
    entry.st_blocks = 1
    
    if value is None:
      entry.st_mode = stat.S_IMODE(datastat.st_mode) | stat.S_IFLNK
    elif isinstance(value, str) or isinstance(value, int) or isinstance(value, float):
      entry.st_mode = stat.S_IMODE(datastat.st_mode) | stat.S_IFREG
    elif isinstance(value, list):
      entry.st_mode = datastat.st_mode
    elif isinstance(value, dict):
      entry.st_mode = value.get('st_mode', None) or self.data.stat().st_mode
    
    entry.st_size = len(str(str(value) + '\n').encode('utf8'))
    entry.st_nlink = len(self._get_rows(lambda node: node.get('id', '') == inode))
    
    if value is None or not isinstance(value, dict):
      value = {}
    entry.st_uid = value.get('st_uid', None) or datastat.st_uid
    entry.st_gid = value.get('st_gid', None) or datastat.st_gid
    entry.st_rdev = value.get('st_rdev', None) or datastat.st_rdev
    
    return entry
  
    
  def readlink(self, inode, ctx):
    log.info('ino: %d', inode)
    row = self._get_row(lambda node: node.get('id', '') == inode)
    if isinstance(row['target'], str):
      return os.path.relpath(row['target'], row['path']).encode('utf8')
    else:
      return self._row_path(row).encode('utf8')


  def opendir(self, inode, ctx):
    log.info('ino: %d', inode)
    return inode


  def readdir(self, inode, off):
    if off == 0:
      off = -1
    
    if off <= 0:
      log.info('ino: %d off: %d', inode, off)
      rows = self._load_rows(inode, off)
      for row in rows:
        name = os.path.basename(self._row_path(row)).encode('utf8')
        yield (name, self.getattr(row['id'], None, row), row['id'])

      
  def unlink(self, inode_p, name,ctx):
    log.info('ino: %d', inode_p)
    entry = self.lookup(inode_p, name)

    if stat.S_ISDIR(entry.st_mode):
      raise FUSEError(errno.EISDIR)

    self._remove(inode_p, name, entry)
    self.wd.refresh()


  def rmdir(self, inode_p, name, ctx):
    log.info('ino: %d', inode_p)
    entry = self.lookup(inode_p, name)

    if not stat.S_ISDIR(entry.st_mode):
      raise FUSEError(errno.ENOTDIR)

    self._remove(inode_p, name, entry)
    self.wd.refresh()
    return (entry.st_ino, entry)


  def _remove(self, inode_p, name, entry):
    log.info('ino: %d name: %s', inode_p, name)
    path_p = self._row_path(self._get_row(lambda node: node.get('id', '') == entry.st_ino))
    if len(self.data.match(path_p + '/*')) > 0:
      raise FUSEError(errno.ENOTEMPTY)
    name, index = self._name_index(name, inode_p)
    row = self._get_row(lambda node: node.get('name', '') == name \
      and node.get('nameindex', '') == index \
      and node.get('pid', '') == inode_p)
    log.info('path: %s', self._row_path(row))
    self.data.remove(self._row_path(row))
    for n in self._get_rows(lambda node: node.get('pid', '') == node['pid'] and node.get('index') > row['index']):
      n['index'] = n['index'] - 1

      
  def symlink(self, inode_p, name, target, ctx):
    log.info('ino: %d', inode_p)
    mode = (stat.S_IFLNK | stat.S_IRUSR | stat.S_IWUSR | stat.S_IXUSR |
        stat.S_IRGRP | stat.S_IWGRP | stat.S_IXGRP |
        stat.S_IROTH | stat.S_IWOTH | stat.S_IXOTH)
    self.wd.refresh()
    return self._create(inode_p, name, mode, ctx, target=target)

  def rename(self, inode_p_old, name_old, inode_p_new, name_new, ctx):
    log.info('old: %d new: %d', inode_p_old, inode_p_new)
    entry_old = self.lookup(inode_p_old, name_old)
    name_old, index_old = self._name_index(name_old, inode_p_old)
    name_new, index_new = self._name_index(name_new, inode_p_new)
    
    try:
      entry_new = self.lookup(inode_p_new, name_new)
    except FUSEError as exc:
      if exc.errno != errno.ENOENT:
        raise
      target_exists = False
    else:
      target_exists = True

    if target_exists:
      self._replace(inode_p_old, name_old, inode_p_new, name_new,
              entry_old, entry_new)
    else:
      row = self._get_row(lambda node: node.get('name','') == name_old and node.get('index','') == index_old and node.get('pid','') == inode_p_old)
      target = self._get_row(lambda node: node.get('id','') == inode_p_new)['path']
      path_new = target + '/' + name_new.decode()
      self.data.move(self._row_path(row), path_new)
      row['path'] = path_new
      row['name'] = name_new
      row['pid'] = inode_p_new
      row['index'] = index_new
      row['nameindex'] = index_new
    self.wd.refresh()

  def _replace(self, inode_p_old, name_old, inode_p_new, name_new,
         entry_old, entry_new):
    log.info('old: %d new: %d', inode_p_old, inode_p_new)
    if len(self._get_rows(lambda node: node.get('pid', '') == entry_new.st_ino)) > 0:
      raise FUSEError(errno.ENOTEMPTY)
    
    row = self._get_row(lambda node: node.get('id','') == entry_old.st_ino)
    path_new = self._row_path(self._get_row(lambda node: node.get('id','') == entry_new.st_ino))
    self.data.move(self._row_path(row), path_new)
    row['pid'] = inode_p_new
    row['path'] = path_new
    self.wd.refresh()


  def link(self, inode, new_inode_p, name_new, ctx):
    log.info('ino: %d p: %d name: %s', inode, new_inode_p, new_name)
    name_new, index_new = self._name_index(name_new, new_inode_p)
    new_p = self._get_row(lambda node: node.get('id', '') == new_inode_p)
    entry_p = self.getattr(None, None, new_p)
    if entry_p.st_nlink == 0:
      log.warn('Attempted to create entry %s with unlinked parent %d',
           name_new, new_inode_p)
      raise FUSEError(errno.EINVAL)
    row = self._get_row(lambda node: node.get('id', '') == inode)
    self.inode_count += 1
    self.nodemap.append({'rowid': len(self.nodemap), 'name': name_new, 'id': self.inode_count, 'pid': new_inode_p, 'path': row['path'], 'nameindex': index_new, 'index': index_new, 'target': None, 'xattrs': {}})
    self.inode_lookup_count[inode] += 1
    self.wd.refresh()
    return self.getattr(inode)

  def setattr(self, inode, attr, fields, fh, ctx):
    log.info('ino: %d attr: %s', inode, attr)
    row = self._get_row(lambda node: node.get('id', '') == inode)
    path = self.data._file_path(self._row_path(row))
    
    try:
      if fields.update_size:
        path, data = self.data.get(path)
        if data is None:
          data = b''
        if isinstance(data, str):
          if len(data) < attr.st_size:
            data = data + b'\0' * (attr.st_size - len(data))
          else:
            data = data[:attr.st_size]
          self.data.set(path, data)
        
      if fields.update_mode:
        os.chmod(path, fields.update_mode)

      if fields.update_uid:
        os.chown(path, fields.update_uid, os.stat(path).st_gid)

      if fields.update_gid:
        os.chown(path, os.stat(path).st_uid, fields.update_gid)
      
      if fields.update_atime:
        os.utime(path, (fields.update_atime, os.stat(path).st_mtime))
        
      if fields.update_mtime:
        os.utime(path, (os.stat(path).st_atime, fields.update_mtime))
    except:
      raise(FUSEError(errno.EACCES))
    
    return self.getattr(inode)
  
  def setxattr(self, inode, name, value, ctx):
    log.info('ino: %d name: %s value: %s', inode, name.decode(), value.decode())
    node = self._get_row(lambda node: node.get('id', '') == inode)
    if os.path.exists(node['path']):
      try:
        xattr.setxattr(node['path'], name, value)
      except:
        pass
    else:
      try:
        xattrs = node['xattrs']
        xattrs[name] = value
      except:
        pass
    self.wd.refresh()
    
  def getxattr(self, inode, name, ctx):
    log.info('ino: %d name: %s', inode, name.decode())
    node = self._get_row(lambda node: node.get('id', '') == inode)
    if os.path.exists(node['path']):
      try:
        return xattr.getxattr(node['path'], name).encode('utf8')
      except:
        pass
    else:
      xattrs = node['xattrs']
      try:
        return xattrs[name]
      except:
        pass
    return b''
  
  def listxattr(self, inode, ctx):
    log.info('ino: %d', inode)
    node = self._get_row(lambda node: node.get('id', '') == inode)
    if os.path.exists(node['path']):
      try:
        return [e.encode('utf8') for e in xattr.listxattr(node['path'])]
      except:
        pass
    else:
      try:
        xattrs = node['xattrs']
        return [e for e in xattrs]
      except:
        pass
  
  def removexattr(self, inode, name, ctx):
    log.info('ino: %d name: %s', inode, name.decode())
    node = self._get_row(lambda node: node.get('id', '') == inode)
    if os.path.exists(node['path']):
      try:
        xattr.removexattr(node['path'], name.decode())
      except:
        pass
    else:
      try:
        xattrs = node['xattrs']
        del xattrs[name.decode()]
      except:
        pass
    self.wd.refresh()
    
    
  def mknod(self, inode_p, name, mode, rdev, ctx):
    return self._create(inode_p, name, mode, ctx, rdev=rdev)

  def mkdir(self, inode_p, name, mode, ctx):
    return self._create(inode_p, name, mode, ctx)

  def statfs(self, ctx):
    log.info('call')
    stat_ = llfuse.StatvfsData()

    stat_.f_bsize = 512
    stat_.f_frsize = 512
    
    datastat = self.data.stat()
    
    size = datastat.st_size
    stat_.f_blocks = 512
    stat_.f_bavail = max(stat_.f_blocks - (size // stat_.f_frsize), 0)
    stat_.f_bfree = stat_.f_bavail
   
    stat_.ffiles = len(self.nodemap)
    stat_.f_ffree = 100000
    stat_.f_favail = max(stat_.f_ffree - stat_.ffiles, 0)
    
    return stat_

  def open(self, inode, flags, ctx):
    log.info('ino: %d', inode)
    # Yeah, unused arguments
    #pylint: disable=W0613
    self.inode_open_count[inode] += 1

    # Use inodes as a file handles
    return inode

  def access(self, inode, mode, ctx):
    log.info('ino: %d', inode)
    # Yeah, could be a function and has unused arguments
    #pylint: disable=R0201,W0613
    self.wd.refresh()
    return True

  def create(self, inode_parent, name, mode, flags, ctx):
    #pylint: disable=W0612
    entry = self._create(inode_parent, name, mode, ctx)
    self.inode_open_count[entry.st_ino] += 1
    return (entry.st_ino, entry)

  def _create(self, inode_p, name, mode, ctx, rdev=0, target=None):
    log.info('ino: %d name: %s target: %s', inode_p, name, target)
    
    name = self._name_subst(name, 'last()+1')
    if self.getattr(inode_p).st_nlink == 0:
      log.warn('Attempted to create entry %s with unlinked parent %d',
           name, inode_p)
      raise FUSEError(errno.EINVAL)
    
    now_ns = int(time() * 1e9)
    parent = self._get_row(lambda node: node.get('id', '') == inode_p)
    
    if stat.S_ISDIR(mode):
      value = {}
    else:
      value = ""
    
    path = self._row_path(parent, force=True) + '/' + name.decode()
  
    if target:
      target = self._get_row(lambda node: node.get('id', '') == target)['path']
    else:
      target = None
      
    try:
      path, value = self.data.set(path, value)
      basename = os.path.basename(path)
      name, index = self._name_index(basename)
      path = os.path.dirname(path) + '/' + name.decode()
      self.inode_count += 1
      log.info('append: ino: %d path: %s index: %d value: %s', self.inode_count, path, index, value)
      self.nodemap.append({'rowid': len(self.nodemap), 'name': name, 'id': self.inode_count, 'pid': inode_p, 'path': path, 'nameindex': index, 'index': index, 'target': target, 'xattrs': {}})
      self.CREATED = True
      self.inode_lookup_count[self.inode_count] += 1
      self.wd.refresh()
      return self.getattr(self.inode_count, None, self.nodemap[-1], 0)
    except FUSEError:
      raise
    else:
      pass

  def read(self, fh, offset, length):
    log.info('read: ino: %d', fh)
    row = self._get_row(lambda node: node.get('id', '') == fh)
    path, data = self.data.get(self._row_path(row))
    
    if data is None:
      data = b''
    if isinstance(data, bytes):
      data = data.decode()
      data = data[offset:offset+length] + '\n'
      return data.encode('utf8')
    elif isinstance(data, str):
      data = data[offset:offset+length] + '\n'
      return data.encode('utf8')

  def write(self, fh, offset, buf):
    log.info('ino: %d', fh)
    temp = False
    row = self._get_row(lambda node: node.get('id', '') == fh)
    path = self._row_path(row, True)
    path, data = self.data.get(path)
    if data is None:
      data = ''
    elif isinstance(data, bytes):
      data = data.decode()
    data = data[:offset] + buf.decode('unicode_escape')
    li = data.rsplit('\n', 1)
    data = ''.join(li)
    path, value = self.data.set(path, data)
    self.wd.refresh()
    return len(buf)

  def releasedir(self, fh):
    log.info('ino: %d', fh)

  def release(self, fh):
    log.info('ino: %d', fh)
    self.inode_open_count[fh] -= 1
    
    if self.inode_open_count[fh] == 0:
      del self.inode_open_count[fh]
      if self.getattr(fh).st_nlink == 0:
        self.del_rows(lambda node: node.get('id', '') == fh)
        
  def fsync(self, fh, datasync=False):
    log.info('ino: %d', fh)
    
  def fsyncdir(self, fh, datasync=False):
    log.info('ino: %d', fh)

class NoUniqueValueError(Exception):
  def __str__(self):
    return 'Query generated more than 1 result row'


class NoSuchRowError(Exception):
  def __str__(self):
    return 'Query produced 0 result rows'

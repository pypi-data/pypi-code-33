
# Capabilities in this module will only
# be made available if you have fusepy installed.

# sudo pip3 install fusepy

# We can return errors by raising
# OSError(number, 'unused description')
# where number comes from these header files
# https://github.com/torvalds/linux/blob/master/include/uapi/asm-generic/errno.h
# https://github.com/torvalds/linux/blob/master/include/uapi/asm-generic/errno-base.h

from __future__ import with_statement

import os
import sys
import errno
import stat
import time
import datetime
import functools

import bb_unsucked

from fuse import FUSE, FuseOSError, Operations


class BBFS(Operations):
    def __init__(self, bb_unsucked_instance):
        self.bb = bb_unsucked_instance
        self.open_file_objects = [] # index will be fh
        self.path_to_fh = {} # string keys point to integer indexes of open_file_objects

    # # Filesystem methods
    # # ==================

    # def access(self, path, mode):
    #     full_path = self._full_path(path)
    #     if not os.access(full_path, mode):
    #         raise FuseOSError(errno.EACCES)

    # def chmod(self, path, mode):
    #     full_path = self._full_path(path)
    #     return os.chmod(full_path, mode)

    # def chown(self, path, uid, gid):
    #     full_path = self._full_path(path)
    #     return os.chown(full_path, uid, gid)

    @functools.lru_cache(maxsize=128) # honestly cheating
    def getattr(self, path, fh=None):
        parent_path = os.path.dirname(path)
        base_name = os.path.basename(path)
        now_s = int(time.time())
        
        obj = None
        try:
          obj_idx = self.open(path, None)
          obj = self.open_file_objects[obj_idx]
        except Exception as ex:
          #print(ex)
          pass
        
        st_size = 0
        if isinstance(obj, bb_unsucked.BBAnnouncement):
          st_size = len(obj.text.encode("utf-8"))
        elif isinstance(obj, bb_unsucked.BBFile):
          if obj.size > -1:
            st_size = obj.size
          else:
            # Choose a big number (25mb) so applications will read something
            st_size = 25 * 1024 * 1024
        elif isinstance(obj, bb_unsucked.BBGradeReport):
          if base_name == "grades.txt":
            st_size = len(obj.txt_table().encode("utf-8"))
          elif base_name == "grades.csv":
            st_size = len(obj.csv_table().encode("utf-8"))
        
        attributes = {
          'st_atime': now_s, # last access time
          'st_ctime': now_s, # last status change time
          'st_gid': os.getgid(),   # group id of owner
          # See https://jameshfisher.com/2017/02/24/what-is-mode_t.html
          'st_mode': stat.S_IFREG | stat.S_IRUSR | stat.S_IWUSR ,
          
          'st_mtime': now_s,
          'st_nlink': 1, # number of hard links
          'st_size': st_size, # total size in bytes
          'st_uid': os.getuid()
        }
        # Modify defaults based on path, basename
        if parent_path == "/" or os.path.dirname(parent_path) == "/":
          attributes['st_mode'] = stat.S_IFDIR | stat.S_IRUSR | stat.S_IWUSR | stat.S_IXUSR
          attributes['st_size'] = 0
        
        return attributes

    @functools.lru_cache(maxsize=128) # honestly cheating
    def readdir(self, path, fh):
        parent_path = os.path.dirname(path)
        base_name = os.path.basename(path)
        dirents = ['.', '..']
        if len(path) < 2: # == "/"
          for c in self.bb.classes():
            if c.is_current():
              dirents.append(c.file_name())
            else:
              dirents.append("."+c.file_name())
        elif parent_path == "/":
          # path != "/", this is a class, list it's contents
          class_id = base_name.split("_")[0]
          links = self.bb.get_class_links(class_id)
          for link in links:
            #dirents.append(path+"/"+link["text"])
            dirents.append(
              bb_unsucked.sanitize_for_use_in_filesystem(link["text"])
            )
        elif os.path.dirname(parent_path) == "/":
          # Wants to list items under a class (base_name == name of link, like "Syllabus")
          class_dir_name = os.path.basename(parent_path)
          class_id = class_dir_name.split("_")[0]
          
          items = self.bb.get_class_link_contents(class_id, base_name)
          
          if items != None:
            for item in items:
              if isinstance(item, bb_unsucked.BBAnnouncement):
                dirents.append(item.file_name())
                
              elif isinstance(item, bb_unsucked.BBFile):
                dirents.append(item.file_name())
                
              elif isinstance(item, bb_unsucked.BBGradeReport):
                dirents.append("grades.txt") # These will be handled specially when
                dirents.append("grades.csv") # the /cs300/* element contains the word "grade"
                
              else:
                dirents.append(str(item))
        
        return dirents

    # def readlink(self, path):
    #     pathname = os.readlink(self._full_path(path))
    #     if pathname.startswith("/"):
    #         # Path name is absolute, sanitize it.
    #         return os.path.relpath(pathname, self.root)
    #     else:
    #         return pathname

    # def mknod(self, path, mode, dev):
    #     return os.mknod(self._full_path(path), mode, dev)

    # def rmdir(self, path):
    #     full_path = self._full_path(path)
    #     return os.rmdir(full_path)

    # def mkdir(self, path, mode):
    #     return os.mkdir(self._full_path(path), mode)

    #def statfs(self, path):
        # stats = {
        #   'f_bavail': 0,
        #   'f_bfree': 0,
        #   'f_blocks': 0,
        #   'f_bsize': 0,
        #   'f_favail': 0,
        #   'f_ffree': 0,
        #   'f_files': 0,
        #   'f_flag': 0,
        #   'f_frsize': 0,
        #   'f_namemax'
        # }
        
        # return stats

    # def unlink(self, path):
    #     return os.unlink(self._full_path(path))

    # def symlink(self, name, target):
    #     return os.symlink(name, self._full_path(target))

    # def rename(self, old, new):
    #     return os.rename(self._full_path(old), self._full_path(new))

    # def link(self, target, name):
    #     return os.link(self._full_path(target), self._full_path(name))

    # def utimens(self, path, times=None):
    #     return os.utime(self._full_path(path), times)

    # File methods
    # ============

    def open(self, path, flags):
        path_split = str(path).split("/") # will break on windows
        if len(path_split) < 4:
          raise OSError(21, 'is a directory')
        elif len(path_split) == 4:
          # Check if we have this item open already
          if path in self.path_to_fh:
            return self.path_to_fh[path] # returns a number
          
          # Serve one file under a course link (like cs417/syllabus/syllabus.pdf)
          file_name = path_split[3]
          sidebar_link_name = path_split[2]
          course_id = path_split[1].split("_")[0]
          file_obj = self.bb.get_a_class_link_content_file(course_id, sidebar_link_name, file_name)
          if file_obj == None:
            raise OSError(2, 'no such file')
          else:
            self.open_file_objects.append(file_obj)
            new_fh = len(self.open_file_objects)-1 # index of file_obj
            self.path_to_fh[path] = new_fh
            return new_fh
          
        else:
          raise OSError(42, 'no message of desired type (aka unimplemented for now)')
        

    # def create(self, path, mode, fi=None):
    #     full_path = self._full_path(path)
    #     return os.open(full_path, os.O_WRONLY | os.O_CREAT, mode)

    def read(self, path, length, offset, fh):
        if fh >= len(self.open_file_objects):
          raise OSError(5, 'i/o error')
        
        fh_obj = self.open_file_objects[fh]
        
        if isinstance(fh_obj, bb_unsucked.BBAnnouncement):
          ann_bytes = fh_obj.text.encode("utf-8")
          return ann_bytes[offset:min(offset+length, len(ann_bytes))]
          
        elif isinstance(fh_obj, bb_unsucked.BBFile):
          r = self.bb.session.get(fh_obj.download_url, stream=True)
          if r.status_code != 200:
            raise OSError(5, 'i/o error')
          
          all_bytes = bytes([])
          for chunk in r.iter_content(1024):
            all_bytes += chunk
          
          return all_bytes[offset:min(offset+length, len(all_bytes))]
        
        elif isinstance(fh_obj, bb_unsucked.BBGradeReport):
          file_name = os.path.basename(path)
          payload_s = ""
          if file_name == "grades.txt":
            payload_s = fh_obj.txt_table()
          elif file_name == "grades.csv":
            payload_s = fh_obj.csv_table()
          else:
            raise OSError(5, 'i/o error')
          
          grade_bytes = payload_s.encode("utf-8")
          return grade_bytes[offset:min(offset+length, len(grade_bytes))]
        
        else:
          return str(fh_obj).encode("utf-8")

    # def write(self, path, buf, offset, fh):
    #     os.lseek(fh, offset, os.SEEK_SET)
    #     return os.write(fh, buf)

    # def truncate(self, path, length, fh=None):
    #     full_path = self._full_path(path)
    #     with open(full_path, 'r+') as f:
    #         f.truncate(length)

    def flush(self, path, fh):
        return 0

    def release(self, path, fh):
        #self.open_file_objects[fh] = None # meh
        # we actually never release allocated memory because caching is awesome.
        # Whoops?
        pass

    def fsync(self, path, fdatasync, fh):
        return 0 # success for everybody


def main(mountpoint, bb_unsucked_instance):
    FUSE(BBFS(bb_unsucked_instance), mountpoint, nothreads=True, foreground=True)





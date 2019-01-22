

# Capabilities in this module will only
# be made available if you have pyftpdlib installed.

# sudo pip3 install pyftpdlib

from pyftpdlib.authorizers import DummyAuthorizer
from pyftpdlib.handlers import FTPHandler
from pyftpdlib.servers import FTPServer
from pyftpdlib.filesystems import AbstractedFS

import os
import sys
import errno
import stat
import time
import datetime
import functools

import bb_unsucked

# https://pyftpdlib.readthedocs.io/en/latest/

# We store bb_unsucked_instance as a global because
# I don't see a nice way of getting it passed to BB_FTP_FS.__init__
bb = None

class BB_FTP_FS(AbstractedFS):
  def __init__(self, root, cmd_channel):
    global bb
    AbstractedFS.__init__(self, root, cmd_channel)
    self.bb = bb
    self.open_file_objects = [] # index will be fh
    self.path_to_fh = {} # string keys point to integer indexes of open_file_objects

  def ftpnorm(self, ftppath):
    return os.path.join(self.cwd, ftppath)
  
  def validpath(self, path):
    # TODO class cache lookup?
    return True
  
  def mkstemp(self, suffix='', prefix='', dir=None, mode='wb'):
    raise OSError(42, 'no message of desired type (aka unimplemented for now)')
  
  def mkdir(self, path):
    raise OSError(42, 'no message of desired type (aka unimplemented for now)')
  
  def chdir(self, path):
    self.cwd = self.ftpnorm(path)
  
  def mkdir(self, path):
    raise OSError(42, 'no message of desired type (aka unimplemented for now)')
    # unsupported at the moment
  
  def rmdir(self, path):
    raise OSError(42, 'no message of desired type (aka unimplemented for now)')
  
  def remove(self, path):
    raise OSError(42, 'no message of desired type (aka unimplemented for now)')
  
  def rename(self, src, dst):
    raise OSError(42, 'no message of desired type (aka unimplemented for now)')
  
  def chmod(self, path, mode):
    raise OSError(42, 'no message of desired type (aka unimplemented for now)')
  
  def stat(self, path): # TODO
    raise OSError(42, 'no message of desired type (aka unimplemented for now)')
  
  def utime(self, path, timeval):
    return 0
  
  def lstat(self, path):
    return self.stat(path)
  
  def isfile(self, path):
    path = self.ftpnorm(path)
    number_pieces = path.split("/")
    return len(number_pieces) > 3 # all things 4 deep and more are files
  
  def islink(self, path):
    return False
  
  def isdir(self, path):
    return not self.isfile(path)
  
  def listdirinfo(self, path):
    return self.listdir(path)
  
  def listdir(self, path):
    path = self.ftpnorm(path)
    print("listdir("+str(path)+")")
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
  
  def open(self, path, mode):
    path_split = str(path).split("/")
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
        fh_idx = len(self.open_file_objects)-1 # index of file_obj
        class ReadableObj():
          def __init__(self, ftp_fs_inst, fh_idx):
            self.ftp_fs_inst = ftp_fs_inst
            self.fh_idx = fh_idx
            self.closed = False
            self.name = "virt_file_index_{}".format(fh_idx)
          
          def read(self, buffer_size):
            if self.closed:
              return None
            self.closed = True # for the moment you wont be able to move more than 65,000 bytes  
            return self.ftp_fs_inst.read(self.fh_idx, buffer_size)
        
        new_fh = ReadableObj(self, fh_idx)
        self.path_to_fh[path] = new_fh
        return new_fh
      
    else:
      raise OSError(42, 'no message of desired type (aka unimplemented for now)')
  
  def read(self, fh, length):
    offset = 0
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

def main(addr_port_tuple, bb_unsucked_instance):
  global bb
  bb = bb_unsucked_instance
  print(addr_port_tuple)
  authorizer = DummyAuthorizer()
  authorizer.add_anonymous("/", perm="elradfmw")
  
  handler = FTPHandler
  handler.authorizer = authorizer
  handler.abstracted_fs = BB_FTP_FS
  
  server = FTPServer(addr_port_tuple, handler)
  server.serve_forever()



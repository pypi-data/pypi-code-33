import os
import sys
import re
import hashlib
import glob
import gzip

from shutil import copyfile,rmtree
from stat import * 
import time

def rm_folder(folder_name):
  rmtree(folder_name,ignore_errors=True)
    
def mk_folder(folder_name) :
  if is_file_exists(folder_name) == False :
    os.makedirs(folder_name, exist_ok=True)

def get_file_folder(file_path) :
  return os.path.dirname (file_path)
  
  
def clean_folder(folder_name):
  if is_file_exists(folder_name) :
    for the_file in os.listdir(folder_name):
      file_path = os.path.join(folder_name, the_file)
      if   os.path.isfile(file_path) : rm_file(file_path)
      elif os.path.isdir(file_path)  : rm_folder(file_path)
  else:
    mk_folder (folder_name)
  
def is_file_exists(file_name):
  return os.path.exists(file_name)
  
def copy_file(src_file,dest_file):
  if is_file_exists(src_file) :  copyfile(src_file,dest_file)    
  
def rm_file(file_name) :
  if os.path.isfile(file_name): 
    os.remove(file_name)
    
def write_file(file_name, text, mode='w', is_new = False):
  file_folder = get_file_folder(file_name)
  if is_file_exists(file_folder) == False: mk_folder(file_folder)
    
  if is_new == True: rm_file(file_name)
  with open(file_name, mode) as fh:
    fh.write(text)

def write_log(file_name, text, is_new = False):
  write_file(file_name=file_name, text=text + "\n", mode='a', is_new=is_new)
    
def read_file(file_name, return_type='str'):
  if return_type == 'str' :
    return open(file_name, 'r').read()
    
  if return_type == 'list' :
    return open(file_name, 'r').readlines() 
    
def get_md5(file_name) :  
  hasher = hashlib.md5()
  with open(file_name, 'rb') as fh:
    buf = fh.read()
    hasher.update(buf)
  return (hasher.hexdigest())

  
def is_file (file) :
  return os.path.isfile(file) 

def is_folder (file) :
  return os.path.isdir(file) 
  
def check_type(full_path):
  if is_file_exists(full_path) : 
    if is_file(full_path) : 
      return 'file'
    elif is_folder(full_path) :  
      return 'dir'
  else:
    return None
  
def gen_files(folder, ext = '', recursive=True, type='all') :
  for f in glob.iglob(folder + '/**/*' + ext , recursive=recursive):
    if os.name=='nt':  
      f = f.replace('\\','/').replace('//','/')
    if type=='all' : 
      yield f
    elif check_type(f) == type : 
      yield f

def get_files(folder, ext='', recursive=True, type='all') : 
  files = []
  for f in gen_files(folder=folder, ext = ext, recursive=recursive, type=type):
    files.append(f)
  return files

def get_file_info(file_name) :
  if is_file_exists(file_name):
    st = os.stat(file_name)
    return { "size" : int(st[ST_SIZE]), "access_time" : st[ST_ATIME] }
  else:
    return None
  
def get_folder_info(folder, recursive=True ):
  total_size  = 0
  total_count = 0
  files = get_files(folder=folder, recursive=recursive)
  total_count = len(files)
  for f in files : 
    total_size += get_file_info(f)["size"]
  
  return (total_count, total_size)  
  

def unzip(gzfile) :
  fgz = gzip.GzipFile(gzfile, 'rb')
  binary_content = fgz.read()
  fgz.close()
  return binary_content


  
  
if __name__ == "__main__":
  #print (len( get_files (folder="R:/", type='file')))
  
  for f in gen_files (folder="R:/", type='file'):
    print (f)
  

    
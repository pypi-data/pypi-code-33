#!/usr/bin/env python
# -*- coding:utf-8 -*-⏎

from __future__ import print_function
import sys
import os
import json
import time
import hashlib
import shutil
import datetime

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~5~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~8
if sys.version_info<(3,0,0):
    reload(sys)
    sys.setdefaultencoding('utf8')

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~5~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~8
def extract_ext(fn, lowcase=True):
    if not fn: return False
    ext = os.path.splitext(fn)[1]
    if len(ext) > 0 and ext[0] == '.': ext = ext[1:]
    if lowcase: ext = ext.lower()
    return ext

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~5~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~8
def is_movie(fn):
    ext = extract_ext(fn)
    if not ext: return False
    if ext in ("mp4", "mkv", "wmv", "avi"): return True
    else: return False

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~5~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~8
def is_image(fn):
    ext = extract_ext(fn)
    if not ext: return False
    if ext in ("jpg", "png", "gif", "bmp"): return True
    else: return False

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~5~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~8
def is_music(fn):
    ext = extract_ext(fn)
    if not ext: return False
    if ext in ("mp3", "wav", "flac"): return True
    else: return False

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~5~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~8
def is_text(fn):
    ext = extract_ext(fn)
    if not ext: return False
    if ext in ("txt", "md", "ini", "json", "c", "cpp", "h", "py", "java"): return True
    else: return False

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~4~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~8
def check_filter(finfo, filter_dict):
    if not filter_dict:
        return True

    if "ext" in filter_dict:
        if finfo.ext.lower() != filter_dict["ext"].lower():
            return False

    return True


# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~4~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~8
class FileInfo:
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~4~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~8
    full_fn = None
    fn = None
    path = None
    base = None
    ext = None
    filetype = None
    icon = None
    cstamp = None
    mstamp = None
    cstr = None
    mstr = None
    size = None

    def __init__(self, full_fn=None, path=None, fn=None):
        if full_fn:
            self.full_fn = full_fn
            self.path = os.path.dirname( full_fn )
            self.fn = os.path.basename( full_fn )

        else:
            self.full_fn = os.path.join(path, fn)
            self.path = path
            self.fn = fn

        if not os.path.isfile(self.full_fn):
            return

        b,e = os.path.splitext(self.fn)
        if e.startswith("."):
            e = e[1:]
        self.base = b
        self.ext = e
        self.cstamp = int(os.path.getctime(full_fn))
        self.mstamp = int(os.path.getmtime(full_fn))
        self.cstr = datetime.datetime.fromtimestamp(self.cstamp).strftime("%y.%m.%d %H:%M:%S")
        self.mstr = datetime.datetime.fromtimestamp(self.mstamp).strftime("%y.%m.%d %H:%M:%S")
        self.size = os.path.getsize(full_fn)
        self.size_str_comma = "{:,}".format(self.size)
        self.size_str = get_filesize_str(self.size)
        st = os.stat(full_fn)

        return

    def is_image(self):
        return is_image(self.fn)

    def is_movie(self):
        return is_movie(self.fn)

    def is_music(self):
        return is_music(self.fn)

    def is_text(self):
        return is_text(self.fn)

    def toJson(self):
        return json.dumps(self, default=lambda o: o.__dict__)

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~4~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~8
def get_parent(root):
    if root == "/":
        return None
    return os.path.abspath(os.path.join(root, os.pardir))


# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~4~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~8
def get_file_list(root, recursive=False, ctx=None, verbose=1):
    if verbose >= 3:
        print("get_file_list: %s" % root)

    if not os.path.isdir(root):
        if verbose >= 1:
            print("root is not dir: %s" % root)
        return False

    # init: get all files
    full_fn_list = list()
    if recursive is True:
        for dn, dns, fns in os.walk(root):
            for fn2 in fns:
                full_fn = os.path.join(dn, fn2)
                full_fn_list.append(full_fn)
    else:
        for fn in os.listdir(root):
            full_fn = os.path.join(root, fn)
            if os.path.isfile(full_fn):
                full_fn_list.append( full_fn )

    # filter
    fi_list = list()
    for full_fn in full_fn_list:
        finfo = FileInfo(full_fn=full_fn)
        if ctx and "filter" in ctx:
            if check_filter(finfo, ctx["filter"]):
                fi_list.append( finfo )
            else:
                # filter
                pass
        else:
            fi_list.append( finfo )

    # sort
    if ctx and "sort" in ctx:
        if ctx["sort"] == "full_fn":
            fi_list.sort(key=lambda x: x.full_fn)
        elif ctx["sort"] == "fn":
            fi_list.sort(key=lambda x: x.fn)
        elif ctx["sort"] == "cstamp":
            fi_list.sort(key=lambda x: x.cstamp)
        elif ctx["sort"] == "size":
            fi_list.sort(key=lambda x: x.size)

        if "order" in ctx and ctx["order"] == "desc":
            fi_list.reverse()


    return fi_list


# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~4~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~8
class DirInfo:
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~4~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~8
    full_dn = None
    dn = None
    path = None
    icon = None
    cstamp = None
    mstamp = None
    cstr = None
    mstr = None
    size = None

    def __init__(self, full_dn=None, path=None, dn=None):
        if full_dn:
            self.full_dn = full_dn
            self.path = os.path.dirname( full_dn )
            self.dn = os.path.basename( full_dn )

        else:
            self.full_dn = os.path.join(path, dn)
            self.path = path
            self.dn = dn

        if not os.path.isdir(self.full_dn):
            return

        self.cstamp = int(os.path.getctime(self.full_dn))
        self.mstamp = int(os.path.getmtime(self.full_dn))
        self.cstr = datetime.datetime.fromtimestamp(self.cstamp).strftime("%y.%m.%d %H:%M:%S")
        self.mstr = datetime.datetime.fromtimestamp(self.mstamp).strftime("%y.%m.%d %H:%M:%S")

        return

    def toJson(self):
        return json.dumps(self, default=lambda o: o.__dict__)

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~4~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~8
def is_file(path):
    if os.path.isfile(path):
        return True
    else:
        # broken symlink
        if os.path.islink(path):
            return True
        else:
            return False


# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~4~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~8
def get_dir_list(root, recursive=False, ctx=None, verbose=1):
    if not os.path.isdir(root):
        return False

    full_dn_list = list()
    if recursive is True:
        for dn, dns, fns in os.walk(root):
            for dn2 in dns:
                full_dn = os.path.join(dn, dn2)
                full_dn_list.append(full_dn)
    else:
        for dn in os.listdir(root):
            full_dn = os.path.join(root, dn)
            if os.path.isdir(full_dn):
                full_dn_list.append(full_dn)

    di_list = list()
    for full_dn in full_dn_list:
        dinfo = DirInfo(full_dn=full_dn)
        if ctx and "filter" in ctx:
            if check_filter(dinfo, ctx["filter"]):
                di_list.append( dinfo )
            else:
                # filter
                pass
        else:
            di_list.append( dinfo )

    # sort
    if ctx and "sort" in ctx:
        if ctx["sort"] == "full_dn" or ctx["sort"] == "full_fn":
            di_list.sort(key=lambda x: x.full_dn)
        elif ctx["sort"] == "dn" or ctx["sort"] == "fn":
            di_list.sort(key=lambda x: x.dn)
        elif ctx["sort"] == "cstamp":
            di_list.sort(key=lambda x: x.cstamp)
        elif ctx["sort"] == "size":
            fi_list.sort(key=lambda x: x.size)

        if "order" in ctx and ctx["order"] == "desc":
            di_list.reverse()

    return di_list


#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~⏎
def is_empty_dir(root, verbose=1):
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~⏎
    if verbose >= 1:
        print("is_empty_dir: %s" % (root))

    file_list = get_file_list(root, recursive=False)
    if file_list is False:
        if verbose >= 2:
            print( "false file_list: %s" % root)
        return False
    if len(file_list) > 0:
        if verbose >= 2:
            print( "file more than 0")
        return False

    dir_list = get_dir_list(root, recursive=False)
    if dir_list is False:
        if verbose >= 2:
            print( "false dir_list: %s" % root)
        return False
    if len(dir_list) > 0:
        if verbose >= 2:
            print( "dir more than 0")
        return False

    return True

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~⏎
def del_empty_dir(root, verbose=1):
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~⏎
    if verbose >= 1:
        print("del_empty_dir: %s" % (root))

    if not is_empty_dir(root, verbose):
        return True

    try:
        os.rmdir(root)
    except Exception as e:
        if verbose:
            print("delete error! %s" % (root))
            print("%s" % (e))
        return False
    return True

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~⏎
def del_file(fn, verbose=1):
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~⏎
    if verbose >= 4:
        print("del_file %s" % (fn))

    try:
        os.remove(fn)
    except Exception as e:
        if verbose >= 1:
            print("delete error! %s" % (fn))
            print(e)
        return False
    return True


#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~⏎
def assert_no_file(fn, verbose=1):
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~⏎
    if verbose >= 2:
        print("assert no file %s" % (fn))

    if is_file(fn):
        if verbose >= 2:
            print("asser no file:del")
        if not del_file(fn, verbose=verbose):
            return False

    return True


# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~4~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~8
def move_file(src, tgt, verbose=1):
    if verbose >= 2:
        print("move_file %s -> %s" % (src,tgt))

    try:
        shutil.move(src, tgt)
    except Exception as e:
        if verbose >= 1:
            print("move_file error")
            print(e)
        return False

    return True


#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~⏎
def assert_dir(dn, verbose=1):
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~⏎
    if verbose>=2:
        print("assert_dir : %s" % (dn))

    if os.path.exists(dn):
        if verbose>=2:
            print("already exists: %s" % (dn))
        return True


    if verbose>=2:
        print("try to make dirs: %s" % (dn))
    os.makedirs(dn, exist_ok=True)

    return os.path.exists(dn)


# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~4~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~8
def txtfile2dict(fn):
    d = dict()
    with open(fn,'r') as f:
        for line in f.readlines():
            line = line.strip("\n")
            d[ line ] = True
    return d


# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~4~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~8
def tsvfile2dict(fn, keyid, valueid):
    d = dict()
    with open(fn,'r') as f:
        for line in f.readlines():
            line = line.strip("\n")
            arr = line.split("\t")
            d[ arr[keyid] ] = arr[valueid]
    return d


# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~4~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~8
def get_md5(fname):
    if not os.path.exists(fname):
        return None

    hash_md5 = hashlib.md5()
    with open(fname, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_md5.update(chunk)
    return hash_md5.hexdigest()

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~4~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~8
def get_filesize_str(s):
    if s> 1024 * 1024 * 1024 * 1024: 
        return "%1.2f TB" % (float(s)/1024/1024/1024/1024)
    elif s > 1024 * 1024 * 1024: 
        return "%1.2f GB" % (float(s)/1024/1024/1024)
    elif s > 1024 * 1024: 
        return "%1.2f MB" % (float(s)/1024/1024)
    elif s > 1024:
        return "%1.2f KB" % (float(s)/1024)
    else:
        return "%d B" % (s)


# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~4~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~8
def test():
    if len(sys.argv) != 3:
        print("usage: %s fn-in fn-out" % sys.argv[0])
        return False
    return True


# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~4~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~8
if __name__ == "__main__":
    test()


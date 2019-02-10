# * Copyright (C) 2018 M E Leypold, GPL3-or-later licensed  --------------------|
#
#     greenland.filesystem.tree -- Mapping filesystem state in an object tree.
# 
#     Copyright (C) 2018 M E Leypold
#
#     This program is free software: you can redistribute it and/or modify
#     it under the terms of the GNU General Public License as published by
#     the Free Software Foundation, either version 3 of the License, or
#     (at your option) any later version.
#
#     This program is distributed in the hope that it will be useful,
#     but WITHOUT ANY WARRANTY; without even the implied warranty of
#     MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#     GNU General Public License for more details.
#
#     You should have received a copy of the GNU General Public License
#     along with this program.  If not, see <https://www.gnu.org/licenses/>.
#

# * Imports  -------------------------------------------------------------------|

import os
import stat
from typing import ClassVar, List, Type


# * Exceptions  ----------------------------------------------------------------|

class FSObjectInitError(Exception):
    pass

class FSObjectTypeError(FSObjectInitError):
    pass

class FSObjectRejected(FSObjectInitError):
    pass

# * Filters  -------------------------------------------------------------------|

TypeFSObject = Type['FSObject']

class Filter(object):

    FSObject : ClassVar[TypeFSObject]
    
    def __init__(self, accept = (lambda obj: True), descend = (lambda obj: True) ):
        self.__accept__  = accept
        self.__descend__ = descend
        
    def accept(self,obj):
        return self.__accept__(obj)

    def descend(self,object):
        return self.__descend__(obj)

    def subfilter(self,name):
        return self
        
# * Paths  ---------------------------------------------------------------------|
                 
class PathInfo(object):

    def __init__(self,path,directory,name,root,relpath):
        self.path       = path
        self.directory  = directory
        self.name       = name

        self.root       = root
        self.relpath      = relpath
        
    def extend(self,name):
        return PathInfo(os.path.join(self.path,name),self.path,name,self.root,os.path.join(self.relpath,name))

class RootPathInfo(PathInfo):

    name    = "."
    relpath = "."
    
    def __init__(self,path):
        self.directory = self.path = path


    @property
    def root(self): return self
        
    def extend(self,name):
        return PathInfo(os.path.join(self.path,name),self.path,name,self,name)

# * Tree Nodes  ----------------------------------------------------------------|


class FSObject(object):

    letter     = "?"
    type       = lambda self,_: True

    rejected   = False  # This is the default, overwritten in __init__, except if it is True

    types      : ClassVar[List[TypeFSObject]]

    # @property 
    # def types(self)
    # FSObject.types   = [FSObject,Directory,File]

    
    def __init__(self,pathinfo,stat,filter,parent=None):
        self.stat      = stat
        if not self.check_type(): raise FSObjectTypeError(pathinfo.path,self.letter)

        self.parent       = parent        
        self.pathinfo     = pathinfo
        self.__basename__ = None
        self.__ext__      = None
        
        if not self.rejected: # overwrite class attribute
            self.rejected   = not filter.accept(self)

    def check_type(self):
        return self.type(self.stat.st_mode)

    @property
    def path(self):
        return self.pathinfo.path

    @property
    def relpath(self):
        return self.pathinfo.relpath    

    @property
    def dirname(self):
        return self.pathinfo.directory

    @property
    def name(self):
        return self.pathinfo.name

    def splitext(self):
        if self.__basename__ == None:        
            self.__basename__, ext= os.path.splitext(self.name)
            self.__ext__ = ext[1:]
        return self.__basename__, self.__ext__
    
    @property
    def ext(self):
        _,ext = self.splitext()
        return ext

    @property
    def basename(self):
        basename,_ = self.splitext()
        return basename    
    
    @classmethod
    def create(cls,pathinfo,filter=Filter(),parent=None):

        for Type in reversed(cls.types):
            try:
                obj = Type(pathinfo,os.stat(pathinfo.path),filter,parent)
                if obj.rejected and not obj.is_dir:
                    break
                else:
                    return obj
            except FSObjectInitError:
                pass
        return None
            

    @classmethod
    def create_root(cls,path,filter):
        return cls.create(RootPathInfo(path),filter)


    @classmethod
    def create_subobj(cls,path,name,filter):
        return cls.create(RootPathInfo(path).extend(name),filter)

    
            
    def __str__(self):
        return "{self.letter} {self.path!r}".format(self=self)

    @property
    def is_dir(self):
        return stat.S_ISDIR(self.stat.st_mode)

    @property    
    def is_file(self):
        return stat.S_ISREG(self.stat.st_mode)

class NotDirectory(FSObject):
    pass
        
class RegularFSObject(NotDirectory):
    pass

class SpecialFSObject(NotDirectory):
    pass

class Directory(FSObject):
    
    letter = "D"
    type   = lambda self,statinfo: stat.S_ISDIR(statinfo)

    def __init__(self,pathinfo,stat,filter,parent=None):
        super().__init__(pathinfo,stat,filter,parent)        
        self.filter = filter.subfilter(pathinfo.name)

    def get_children(self, accept = lambda obj: obj.is_dir ):
        for name in os.listdir(self.path):
            child_pathinfo = self.pathinfo.extend(name)
            child   = self.filter.FSObject.create(child_pathinfo,self.filter,parent=self)
            if child != None:
                yield child
    
    @property
    def children(self):
        return ( child for child in self.get_children() if not child.rejected )

    def traverse(self,filter=None):

        if filter != None:
            d = filter.FSObject.create(child_pathinfo,filter)
            assert d.is_dir
            dirs = [d]
        else:
            dirs = [self]

        while len(dirs) > 0:
            d = dirs.pop()
            if not d.rejected:
                yield(d)
            for child in d.get_children():
                if child.is_dir:
                    dirs.append(child)
                else:
                    assert not child.rejected # that's our protocol
                    yield child

            
                
    
class File(RegularFSObject):

    letter = "F"
    type   = lambda self,statinfo: stat.S_ISREG(statinfo)

Filter.FSObject  = FSObject   
FSObject.types   = [FSObject,Directory,File]

# * Find -----------------------------------------------------------------------|

def find( *roots, accept = (lambda obj: True), descend = (lambda obj: True)):
    for rootpath in roots:
        root = FSObject.create(RootPathInfo(rootpath),filter=Filter(accept=accept,descend=descend))
        assert root.is_dir
        print(root.__class__)
        for obj in root.traverse():
            yield obj


def find_files(*roots,accept = (lambda obj: True), accept_parents = False):

    dirs = set()

    def collect_missing_parents(parent, parents):            
        while parent != None:
            if not parent in dirs:
                parents.append(parent)
                dirs.add(parent)
            else:
                return
            parent = parent.parent

    def missing_parents(obj):
        parents = []
        collect_missing_parents(obj.parent, parents)
        return parents

    for obj in find(*roots, accept = (lambda obj: (obj.is_dir) or accept(obj))):
        if obj.is_dir: continue
        if accept_parents:
            for parent in reversed(missing_parents(obj)):
                yield parent
        yield obj
            

# * ----------------------------------------------------------------------------|


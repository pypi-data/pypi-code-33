import os
import stat

class FSObjectInitError(Exception):
    pass

class FSObjectTypeError(FSObjectInitError):
    pass

class FSObjectRejected(FSObjectInitError):
    pass

class Filter(object):

    def accept(self,obj):
        return True

    def descend(self,object):
        return True

    def subfilter(self,name):
        return self
        

class PathInfo(object):

    def __init__(self,path,directory,name):
        self.path       = path
        self.directory  = directory
        self.name       = name

    def extend(self,name):
        return PathInfo(os.path.join(self.path,name),self.path,name)

class RootPathInfo(PathInfo):

    name = "."
    
    def __init__(self,path):
        self.directory = self.path = path
    
class FSObject(object):

    letter     = "?"
    type       = lambda self,_: True

    rejected   = False  # This is the default, overwritten in __init__, except if it is True
    
    def __init__(self,pathinfo,stat,filter):
        self.stat      = stat
        if not self.check_type(): raise FSObjectTypeError(pathinfo.path,self.letter)

        self.pathinfo   = pathinfo

        if not self.rejected: # overwrite class attribute
            self.rejected   = not filter.accept(self)

    def check_type(self):
        return self.type(self.stat.st_mode)

    @property
    def path(self):
        return self.pathinfo.path

    @property
    def dirname(self):
        return self.pathinfo.directory

    @property
    def name(self):
        return self.pathinfo.name    
    
    @classmethod
    def create(cls,pathinfo,filter):
        for Type in reversed(cls.types):
            try:
                return Type(pathinfo,os.stat(pathinfo.path),filter)
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

    def __init__(self,pathinfo,stat,filter):
        super().__init__(pathinfo,stat,filter)
        if self.rejected: raise FSObjectRejected(pathinfo.path,self.letter)
        
class RegularFSObject(NotDirectory):
    pass

class SpecialFSObject(NotDirectory):
    pass

class Directory(RegularFSObject):
    
    letter = "D"
    type   = stat.S_ISDIR

    def __init__(self,pathinfo,stat,filter):
        super().__init__(pathinfo,stat,filter)        
        self.filter = filter.subfilter(pathinfo.name)

    def get_children(self, accept = lambda obj: obj.is_dir ):
        for name in os.listdir(self.path):
            child_pathinfo = self.pathinfo.extend(name)
            child   = self.filter.FSObject.create(child_pathinfo,self.filter)
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
    type   = stat.S_ISREG


FSObject.types   = [FSObject,Directory,File]
Filter.FSObject  = FSObject   


def test_spike():
    pass

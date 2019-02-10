# -*- coding: utf-8 -*-

import copy

def toAutoData(val):
    if type(val) == list:
        return autolist(val)
    elif type(val) == dict:
        return autodict(val)
    else: return val

class emptyitem:
    def __init__(self, parent, key):
        self.parent = parent
        self.key = key

    def __getitem__(self, key):
        return emptyitem(self, key)

    def __setitem__(self, key, val):
        if type(key) == str:
            newdata = autodict()
        elif type(key) == int:
            newdata = autolist()
        else:
            raise TypeError("key type error")
        newdata[key] = val
        self.parent[self.key] = newdata

    def __len__(self):
        return 0

    def __iter__(self):
        return iter([])

    def __contains__(self, item):
        return False

    def keys(self):
        return []
    
    def append(self, item):
        newdata = autolist()
        newdata.append(item)
        self.parent[self.key] = newdata

    def sort(self, *params):
        pass

    def clear(self):
        pass

    def __iadd__(self, val):
        if type(val) == list:
            val = autolist(val)
        return copy.copy(val)

    def __ior__(self, val):
        return val
    
    def __ixor__(self, val):
        return val
    
    def __iand__(self, val):
        return self

    def __isub__(self, val):
        self.parent[self.key] = -val
        return -val

    def __imul__(self, val):
        return self

class autodict(dict):
    empty = emptyitem(None, None)

    def __init__(self, initData = None):
        if isinstance(initData, dict):
            for key in initData.keys():
                dict.__setitem__(self, key, toAutoData(initData[key]))
        elif initData != None:
            raise Exception("Invalid type")

    def aget(self, key, deffunc):
        t = type(key)
        if t == str:
            item = dict.get(self, key, autodict.empty)
            if item != autodict.empty:
                return item
            else:
                if deffunc == None:
                    return emptyitem(self, key)
                else:
                    item = deffunc()
                    dict.__setitem__(self, key, item)
                    return item
        else:
            raise TypeError("autodict key must be str")

    def __getitem__(self, key):
        return self.aget(key, None)

    def __setitem__(self, key, val):
        if type(val) == emptyitem:
            if key in self:
                dict.__setitem__(self, key, None)
            return
        dict.__setitem__(self, key, val)

class autolist(list):
    def __init__(self, initData = None):
        if isinstance(initData, list):
            for item in initData:
                self.append(toAutoData(item))
        elif initData != None:
            raise TypeError("autolist initData must be list")

    def aget(self, key, deffunc):
        t = type(key)
        if t == int:
            if key >= len(self) or list.__getitem__(self, key) == None:
                if deffunc == None:
                    return emptyitem(self, key)
                else:
                    item = deffunc()
                    self[key] = item
                    return item
            return list.__getitem__(self, key)
        elif t == slice:
            return list.__getitem__(self, key)
        else:
            raise TypeError("autolist key must be integer")

    def __getitem__(self, key):
        return self.aget(key, None)

    def __setitem__(self, key, val):
        if type(val) == emptyitem:
            if key < len(self):
                list.__setitem__(self, key, None)
            return
        if key >= len(self):
            for _ in range(0, key - len(self)): self.append(None)
            self.append(val)
        else:
            list.__setitem__(self, key, val)

    def __iadd__(self, val):
        if type(val) == emptyitem:
            return self
        elif not isinstance(val, list):
            raise TypeError("Cannot add autolist to " + str(type(val)))
        list.__iadd__(self, val)
        return self
    
    def __add__(self, val):
        return autolist(list.__add__(self, val))

    def __mul__(self, val):
        a = autolist(self)
        list.__imul__(a, val)
        return a


def defined(obj):
    if obj == None:
        return False
    elif type(obj) == emptyitem:
        return False
    else:
        return True

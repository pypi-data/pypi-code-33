# -*- coding: utf-8 -*-

"""
les foncteurs:
    ils prennent en entrée un objet ou un iterable
    ils retournent un itérable
    ils peuvent s'enchainer comme des pipes (| cad __or__)
    pour les classes
        OBJ
        PSC, NSC
        ATT
        INIT, FIN
    pour les instances
        OPSC, ONSC
        OATT
        CLASS (equivalent à type)
        OINIT, OFIN
    Les foncteurs serviront de base aux queries puis aux querietrees
    options: raise and stop or raise and continue

    ex:
       IDENT(X) | OBJ | OPSC(R) | OFIN => mieux car introduit une nouvelle syntaxe pour un nx d'abstraction sup.
       X.OBJ.OPSC(R).OFIN

TODO: add ordered fonctors
"""

import collections, inspect

def getattrsfromdict(dic):
    return [attr for attr in dic \
            if not attr.startswith('_') \
            and not inspect.isroutine(dic[attr]) \
            and not isinstance(dic[attr], property)]
    
def getattrs(obj, follow_mro=True):
    """
    Return names of public attributes of *obj* throught class hierarchy and
    in respect of declaration order. If obj is a class, *names* are class attributes.
    """
    if obj in (object, type): return []
    obj_attrs = getattrsfromdict(obj.__dict__)
    class_attrs = []
    cls = obj if isinstance(obj, type) else type(obj)
    if follow_mro:
        try:
            class_attrs += getattrs(cls.mro()[1], follow_mro)
        except TypeError: # If we want mro of class of class!
            pass
    class_attrs += getattrsfromdict(cls.__dict__)

    i =  0
    for a in class_attrs:
        if a in obj_attrs:
            i += 1
            continue
        obj_attrs.insert(i, a)
        i += 1

    return obj_attrs
    

def to_iterable(obj):
    """Return obj as an inmutable iterable if necessary, except for str.
       If obj is already an iterable, return obj unchanged.
    """
    if not isinstance(obj, collections.Iterable) \
    or isinstance(obj, str): 
        return (obj,)
    return obj
    
class Fonctor(object):
    def __init__(self, func=None, *args, **kargs):
        self.__func = func if func is not None else lambda x: x
        self.__args = args
        self.__kargs = kargs
    def __or__(self, other):
        return self.__exec(other)
    def __ror__(self, other):
        return self.__exec(other)
    def __call__(self, *args, **kargs):
        self.__args = args
        self.__kargs = kargs
        return self
    def __exec(self, other):
        result = set()
        for l in [self.__func(o, *self.__args, **self.__kargs) for o in to_iterable(other)]:
            for oo in to_iterable(l): result.add(oo)
        return result
        
IDENT = Fonctor()                          
CLASS = Fonctor(type)
attrs = Fonctor(getattrs)

def getvalattrs(obj, attrnames=[]):
    if len(attrnames) != 0:
        return [getattr(obj,a) for a in obj | attrs  if a in attrnames]
    else:
        return [getattr(obj,a) for a in obj | attrs]
    
valattrs = Fonctor(getvalattrs)

# Attention: il peut y avoir un bug difficile à trouver si o fait par exemple:
# "o | valattrs"  à la place de "o | valattrs()". dans ce cas le __ror__
# fait l'exec sans param. Pas propore

# Return objects that belong to classes
OBJOF = Fonctor(lambda obj, *classes: obj if isinstance(obj, classes) else [])






    

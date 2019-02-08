# -*- coding: utf-8 -*-
"""
Utilitaires utilisant hbds ou non.
"""

import collections, warnings
from . import hbds

__all__ = (
    "Cache",
    )

class Cache(collections.MutableSet):
    """
    Implémente un *cache d'objet* comme un *set* python.
    Si un objet est ajouté dans le *cache*, sa classe sera instrumentée
    pour réagir à la modification des attributs (setattr)
    Si cet objet est un objet hbds, il sera également instrumenté
    pour réagir à la création des relations entre objets.

    Par exemple, on définit 2 classes HBDS reliées entre elles:

    >>> class Humain(metaclass=hbds.Class):
    ...     nom = str
    >>> class Voiture(metaclass=hbds.Class):
    ...     type = str
    >>> possede = hbds.Link(Humain, 'possede', Voiture)

    Puis on crée des instances

    >>> h1 = Humain("Jean"); h2 = Humain("Paul")

    Que l'on ajoute à un cache

    >>> cache = Cache((h1, h2))

    Toutes les modifications des attributs et des relations seront notifées:

    >>> h1.nom = "Jean-Paul"
    >>> h2.nom = "Pierre-Paul"
    >>> v1 = Voiture("X"); v2 = Voiture("Y")
    >>> p1 = possede(h1, v1); p2 = possede(h2, v2)

    
    """
    _caching_types = {}
    _caches = []
    def __init__(self, iterable=[]):
        self._cache = set(iterable)
        self._caches.append(self)

    def __contains__(self, obj):
        return obj in self._cache
    def __iter__(self):
        return iter(self._cache)
    def __len__(self):
        return len(self._cache)
    def __del__(self):
        self._caches.remove(self)
    
    def add(self, obj):
        self._cache.add(obj)
        self._instrument(obj)
        
    def discard(self, obj):
        self._cache.discard(obj)
        self._uninstrument(obj)
    
    def _instrument(self, obj):
        cls = type(obj)
        if cls in self._caching_types: return
        
        oldfset =  cls.__setattr__
        def fset(instance, attr, value):
            oldvalue = getattr(instance, attr, None)
            for cache in Cache._caches:
                if instance in cache: 
                    cache.before_setattr(instance, attr, oldvalue )
            oldfset(instance, attr, value)
            for cache in Cache._caches:
                if instance in cache: 
                    cache.after_setattr(instance, attr, value)

        cls.__setattr__ = fset
        self._caching_types[cls] = oldfset

        for R in (cls | hbds.PSC).union( cls | hbds.NSC): # relations in & out
            oldinit = R.__init__
            def init(rel, *args, **kargs):
                oldinit(rel, *args, **kargs)
                self.link(type(rel), args[0], args[1])
            R.__init__ = init
            oldcut = R.cut
            def cut(rel):
                oinit = rel.__oinit__
                ofin = rel.__ofin__
                oldcut(rel)
                self.unlink(type(rel), oinit, ofin)
            type.__setattr__(R, 'cut', cut) # R.cut = cut
                

    def before_setattr(self, obj, attr, old_value):
        warnings.warn("Cache before_setattr() is not Implemented")
        # do nothing in default implementation

    def after_setattr(self, obj, attr, new_value):
        warnings.warn("Cache after_setattr() is not Implemented")
        # do nothing in default implementation

    def link(self, relcls, oinit, ofin):
        warnings.warn("Cache link() is not Implemented")
        # do nothing in default implementation

    def unlink(self, relcls, oinit, ofin):
        warnings.warn("Cache unlink() is not Implemented")
        # do nothing in default implementation
    
    def _uninstrument(self, obj):
        if len([o for cache in Cache._caches for o in cache \
                if type(o) is type(obj)]) == 0:
            fset = self._caching_types[type(obj)]
            type(obj).__setattr__ = fset
        


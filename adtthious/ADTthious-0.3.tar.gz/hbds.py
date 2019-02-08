# -*- coding: utf-8 -*-
"""
The aim of this module is to provide Abstract Data Type (ADT) used to
describe Data Structure in Pythonic fashon.

TODO:
    module doc
    automatic docstring in __init__ methods
    docstring of atts

External references:
 * HBDS: http://pelle.stephane.free.fr/HBDSConseils.htm
 * https://rhettinger.wordpress.com/2011/05/26/super-considered-super/
 * https://blog.ionelmc.ro/2015/02/09/understanding-python-metaclasses/
 * https://docs.python.org/3.6/howto/descriptor.html
 * module attrs (http://www.attrs.org/en/stable/)
 * module leaflet
 * module dataclasses (https://docs.python.org/3/library/dataclasses.html)
   integrate in py3.7
 * https://pypi.org/project/structures/
 * http://mypy.readthedocs.io/en/latest/
"""

import collections, types
from .fonctors import (getattrsfromdict, getattrs,
                      Fonctor, to_iterable, getvalattrs,
                      valattrs, OBJOF, attrs)
from .units import Unit

__all__ = (
    'Att',
    'create_Att',
    'ComposedAtt',
    'Class',
    'ATT',
    'OATT',
    'raise_init',
    'OBJ',
    'keep_objects_relationship',
    'Relation',
    'create_relation',
    'Link',
    'PSC',
    'NSC',
    'INIT',
    'FIN',
    'OPSC',
    'OPSCR',
    'ONSC',
    'ONSCR',
    'OINIT',
    'OFIN',
    'Role',
    )

class Att:
    """
    Used to define a class attribute to provide:
     * existing control
     * type control
     * default value
     * and also mandatory information, docstring and contrainst function.
       at intance level.
    Att is a python descriptor, so must be use as class variable
    in class definition.

    TODO: revoir les contraintes pour utiliser des méthodes
    """
    
    class required:
        """
        Just to tell if Att is mandarory (or required). See Att.__init__.
        """
        pass

    def __init__(self, att_type=None, default=None, mandatory=False,
                 doc=None, constraint=None, unit=None):
        self.type = att_type
        self.mandatory = mandatory
        self.doc = doc
        self.constraint = constraint
        self.name = None
        self.default = self._validate(default)
        if self.type is None and self.default is not None:
            self.type = type(self.default)
        self.unit = unit
        self.classvars = {}
            
    def __get__(self, instance, ownerclass):
        if instance is None:
            for c in ownerclass.__mro__:
                if self.name in c.__dict__:
                    return c.__dict__[self.name]
        if isinstance(instance, type):
            try:
                return self.classvars[instance]
            except KeyError as e:
                msg = "type '%s' use class var already define in its metaclass" \
                      % instance
                # cf. tests.hbds.ClassOfClassTest.test_already_declare_att_in_metaclass
                raise TypeError(msg)
        return instance.__dict__.get(self.name, self.default)
        
    def _validate(self, value):
        if value is None:
            return value
        # try to catch value with type
        if self.type:
            if not isinstance(value, self.type):
                try:
                    value = self.type(value)
                except (ValueError, TypeError):
                    m = "'%s' for '%s'. Should be '%s' instead of '%s'" \
                        % (value, self, self.type, type(value))
                    raise TypeError(m)
        # try to apply contraint
        if self.constraint:
            self.constraint(value)
        return value
    
    def __set__(self, instance, value):
        value = self._validate(value)
        if value is None and self.mandatory:
            raise ValueError("'%s' Att is mandatory. Can't be set to None" % self.name)
        if isinstance(instance, type):
            self.classvars[instance] = value 
        else:
            instance.__dict__[self.name] = value
        
    def __set_name__(self, cls, name):
        self.name = name
        
    def __repr__(self):
        s = "<Att(type=%s, default=%s, mandatory=%s)>" \
            % (self.type, self.default, self.mandatory)
        if self.name is None:
            s = "Not named " + s
        else:
            s += "named %s" % self.name
        return s

class ComposedAtt:
    
    def __init__(self, **attr_defs):
        name = "%s_tmp" % self.__class__.__name__
        self._class = create_class(name, attr_defs)
        L = [v for v in self._class | ATT if v.mandatory and not v.default]
        if len(L) != 0:
            raise AttributeError("Impossible to use mandatory attribute without default value in ComposedAtt")

    def __get__(self, instance, ownerclass):
        if not instance: return self._class()
        return instance.__dict__.setdefault(self._name, self._class())

    def __set__(self, instance, value):
        raise AttributeError("%s '%s' of %s is'nt settable" % \
                    (type(self).__name__, self._name, instance))

    def __set_name__(self, cls, name):
        self._name = name
        self._class.__name__ = "%s_%s" % (self.__class__.__name__, name)


class Class(type):    

    # We use 'clsnamespace' for dictionary product par the interpreter to init
    # a new class. In python doc, we find 'namespace'. In litterature we
    # could find 'clsdict' or also 'attrs'.
    
    @classmethod
    def __prepare__(mcls, name, bases, **kwds):
        # be sure namespace of a new class will keep order of declaration
        return collections.OrderedDict()
    
    def __new__(mcls, clsname, bases, clsnamespace):
        # Warning: clsnamespace MUST BE modified directly
        # It's impossible to use an other dict or a copy
        # else __new__ doesn't run!
        # all (implicit!) explanations are available in python doc metaclass

        # transform python public attributes (and that not method)
        # of the new class to an Att if needed
        for public_att in getattrsfromdict(clsnamespace):
            val = clsnamespace[public_att]

            # to detect embeded class definitions as
            # class C(metclass=Class):
            #   class X(metaclass=Class):  et class X tout cours?
            if isinstance(val, Class): continue

            val = to_iterable(val)
            clsnamespace[public_att] = create_Att(*val)

        # if the new class is not a child of Class,
        # we will make the __init__ method
        parent_classes = [c for b in bases for c in b.__mro__]
        if Class not in parent_classes:
            
            # we create an ordered dictionnary of all inherited Att,
            # indexed by base classes...
            up_attrs_by_bases = collections.OrderedDict()
            for b in bases:
                if b is object: continue
                up_attrs_by_bases[b] = collections.OrderedDict([ \
                (a,getattr(b,a)) for a in getattrs(b) \
                if isinstance(getattr(b,a), Att)] )

            # ... and an another just for new class
            attrs = collections.OrderedDict([(a,clsnamespace[a]) for a in clsnamespace \
                                             if isinstance(clsnamespace[a], Att)])

            # these will be usefull for create __init__ method
            code = mcls._make_init_method(up_attrs_by_bases, attrs)

            # we try to add the __init__ method to new class namespace
            # using 'exec' (please (re)read python doc of metaclass)
            try:
                # __init__ must have the form, for example:
                # class Z(Y, T):
                #    def __init__(self, x=Y.x, y=Y.y, z=z, t=T.t):
                #       Y.__init__(self, x, y)
                #       T.__init__(self, t)
                #       ...
                # Pb is Y and T are just accessible from scope where Z
                # is defined. It can be not necessary global
                # So we set local variables with all base classes
                # to bind names with base classes from locals()
                # I spent a lot of time to find this!
                for i,b in enumerate(bases):
                    exec("%s = bases[i]" % b.__name__)
                exec(code , locals(), clsnamespace)
            except SyntaxError as e:
                e.msg = make_readable_SyntaxError(code, e)
                raise e

        # then we make a instance __setattr__ method
        # to avoid set of undeclare attribute at new class instance level
        def fset(instance, att, val):
            if not att.startswith('_'): # TODO: why do we need private att?
                if not hasattr(type(instance), att):
                    m = "Class instance '%s' has no Att '%s'"
                    raise AttributeError(m % (instance, att))
            if isinstance(instance, type):
                type.__setattr__(instance, att, val)
            else:
                object.__setattr__(instance, att, val)
        clsnamespace['__setattr__'] = fset

        # and finally with create the new class
        newcls = super().__new__(mcls, clsname, bases, clsnamespace)
        return newcls
    
    def __setattr__(cls, att, val):
        if not att.startswith('_'):
            if not hasattr(type(cls), att):
                m = "Class type '%s' has no Att '%s'"
                raise AttributeError(m % (cls, att))
        # super doesn't run here. I don't no why
        #super().__setattr__(att, val)
        type.__setattr__(cls, att, val)
        
    @classmethod
    def _make_init_method(mcls, up_attrs_by_bases, attrs):
        args = make_code_args(up_attrs_by_bases, attrs)
        if args == "": return ""
        code = """def __init__(self, %s):\n""" % args

        for b in up_attrs_by_bases:
            attnames = [a for a in up_attrs_by_bases[b]]
            code += "    %s.__init__(self, %s)\n" % (b.__name__, ', '.join(attnames))

        code += make_attrs_init(attrs)

        return code

        
def make_code_args(up_attrs_by_bases, attrs):
    code_args = []
    for b in up_attrs_by_bases:
        for a in up_attrs_by_bases[b]:
            att = up_attrs_by_bases[b][a]
            code_args.append(make_code_arg(a, att, b.__name__))
    for a in attrs:
        code_args.append(make_code_arg(a, attrs[a]))
        
    args = ', '.join(code_args)
    return args

def make_code_arg(attname, att, basename=""):
    codebase = "%s." % basename if basename != "" else ""
    if att.default is not None:
        code = "%s=%s%s.default" % (attname, codebase, attname)
    elif att.mandatory:
        code = attname
    else:
        code = "%s=None" % attname        
    return code
    
def make_attrs_init(attrs):
    return ''.join(['    self.%s = %s\n' % (a, a) for a in attrs])


def make_readable_SyntaxError(code, exception):
    msg = exception.msg
    msg += " line %d in dynamic created __init__\n" % exception.lineno
    for n, l in enumerate(code.splitlines()):
        msg += ''.join(["%2d: %s\n" % (n+1,l) ])
        if n+1 == exception.lineno:
            msg += "%s^\n" %(' '*(exception.offset+3)) # the 2 line number + ':'
    return msg



def create_Att(*vals):
    """
    Return an *Att* instance from tuple *vals*.
    The tuple is interpreted as parameters of Att in any order
    and it may be empty.
    If tuple does'nt respect Att params, **AttributeError** is raised.

    TODO: add contrainsts
    """
    if len(vals) > 4:
        raise TypeError("Too many args for Att (%d). Must be 4 max" % len(vals))

    # because order is not important, so re-order vals
    typ, default, mandatory, unit = None, None, not Att.required, None
    # manque des tests car il peut y avoir 4 valeurs sans Unit par ex.
    for v in vals:
        if v is Att.required: mandatory = v
        elif isinstance(v, Unit): unit = v
        elif isinstance(v, type): typ = v
        else: default = v

    # vals is already a Att
    if isinstance(default, (Att, ComposedAtt)):
        if len(vals) != 1:
            raise TypeError("Too many Att definition (%d). Use just one" % len(vals))
        return default

    return Att(typ, default, mandatory, unit=unit)

def create_class(name, attr_defs):
    """
    Return class from *name* and *attr_defs* dictionary.
    Do the same thing as instruction:
    class X(metaclass=Class):
        a1 = Att(int, 1)
        a2 = float
    with *name* = 'X' and *attr_defs* = {'a1': Att(int, 1), 'a2': Att(float)}
    see Class and Att definitions.
    """
    meta = {'metaclass': Class }
    def update(clsdic):
        for att, val in attr_defs.items():
            clsdic[att] = val
    return types.new_class(name, kwds=meta, exec_body=update)

ATT = Fonctor(lambda cls: cls | valattrs | OBJOF(Att))

OATT = Fonctor(lambda obj: [getattr(obj, a.name) for a in type(obj) | ATT])

def raise_init(cls):
    """
    Decorate the class *cls* to prevent instance creation. It can be use
    for just create simple type that you don't want to instanciate it.
    >>> @raise_init
    ... class Road: pass
    >>> Road()
    Traceback (most recent call last):
    ...
    TypeError: Instance creation is not allowed for <class 'ADT.hbds.Road'>
    """
    def init(self):
        raise TypeError("Instance creation is not allowed for %s" % cls)
    cls.__init__ = init
    return cls


OBJ = Fonctor(lambda cls: getattr(cls, '__obj__'))

def keep_objects_relationship(cls):
    """
    Decorate the class *cls* to add to it a *__obj__* list to keep track
    of all instances of the class.
    You can use it for a class
    >>> @keep_objects_relationship
    ... class X: pass
    >>> x1 = X(); x2 = X()
    >>> X.__obj__ #doctest: +ELLIPSIS
    [<ADT.hbds.X object at 0x...>, <ADT.hbds.X object at 0x...>]
    
    >>> @keep_objects_relationship
    ... class TerrainType(type): pass
    >>> class X(metaclass=TerrainType): pass
    >>> class Y(metaclass=TerrainType): pass
    >>> TerrainType.__obj__ 
    [<class 'ADT.hbds.X'>, <class 'ADT.hbds.Y'>]

    Usage of *__obj__* is just for tests. It's more pretty to use fonctor OBJ
    >>> L = TerrainType | OBJ  # product en set() with ungaranted order
    >>> X in L and Y in L and len(L) == 2 # 
    True

    Warning: decorator must be use only with classes
    with invariant number of instances because __del__ is not implemented!
    """
    if not hasattr(cls, '__obj__'):
        setattr(cls, '__obj__', [])
        
    oldinit = getattr(cls, '__init__', None)
    def newinit(self, *args, **kargs):
        if oldinit:
            oldinit(self, *args, **kargs)
        cls.__obj__.append(self)
    cls.__init__ = newinit

    # Attention: ne fonctionne pas!
##    olddel = getattr(cls, '__del__', None)
##    def newdel(self):
##        if olddel:
##            olddel(sel)
##        cls.__obj__.remove(self)
##    cls.__del__ = newdel
    
    return cls

"""
Cardinalités des rôles des relations

L: X (n,m) -> (n,m) Y

@noreverse
    pour ne pas implémenter le negative semi cocircuit
    nommer la relation inverse => inverser les psc, nsp

Optimisation de l'acces
    if m == 1:  SC != list

Contrôles relatifs aux cardinalités
    if m is not None: n <= m
    if m is not None: contrôle si len(sc) == m avant création de la relation
    if n != 0:
        => contraintes à la création des objets init et fin
        si ni != 0 => nf == 0 et inversement
        X (2, 3) (0,2) Y
            X(..., y1, y2)
        X(0,2) (1,3) Y
            Y(..., x1)
    m = 'all' => relation avec tous les Y?

"""

class SemiCocircuit:

    # Attention:
    #   * pas d'héritage de liens
    #   * et confusion entre SC d'object et SC de type object
        
    def __init__(self, name):
        self.name = name
        self.sc = []
        self.classvars = {}

    def __get__(self, obj, cls):
        if obj is None:
            # when uses class attribute
            return self.sc
        
        if isinstance(obj, type):
            if obj not in self.classvars:
                self.classvars[obj] = SemiCocircuit(self.name)
            return self.classvars[obj].sc

        if self.name not in obj.__dict__:
            obj.__dict__[self.name] = SemiCocircuit(self.name)
        return obj.__dict__[self.name].sc

    def __set__(self, obj, value):
        raise AttributeError(self.name + " are not settable")


class Relation(Class):

    def __new__(mcls, clsname, bases, clsnamespace):
        if '__cinit__' not in clsnamespace:
            raise TypeError("Relation must define the '__cinit__' class")
        if '__cfin__' not in clsnamespace:
            raise TypeError("Relation must define the '__cfin__' class")
        if '__cards__' not in clsnamespace:
            # set default cardinalities
            clsnamespace['__cards__'] = ((0,'m'),(0,'m'))
        def cut(self):
            type(self).unlink_objects(self)
        clsnamespace['cut'] = cut #lambda l: mcls.unlink_objects(l)

        clsobj = Class.__new__(mcls, clsname, bases, clsnamespace)
        return clsobj

    @classmethod
    def _make_init_method(mcls, up_attrs_by_bases, attrs):
        args = make_code_args(up_attrs_by_bases, attrs)
        if args == "":
            code = """def __init__(self, oinit, ofin):\n"""
        else:
            code = """def __init__(self, oinit, ofin, %s):\n""" % args
        code += "    type(self).link_objects(self, oinit, ofin)\n"
        for b in up_attrs_by_bases:
            attnames = [a for a in up_attrs_by_bases[b]]
            code += "    %s.__init__(self, %s)\n" % (b.__name__, ', '.join(attnames))

        code += make_attrs_init(attrs)
        return code
    
    def __init__(rel, name, bases, clsnamespace):
        super(Relation, rel).__init__(name, bases, clsnamespace)
        rel.create_class_links()

    @property
    def cocircuit(clsrel):
        return SemiCocircuit
    
    def create_class_links(clsrel):
        for cls in (clsrel.__cinit__, clsrel.__cfin__):
            for a in ('__psc__', '__nsc__'):
                if not hasattr(cls, a):
                    setattr(cls, a, clsrel.cocircuit(a))
        clsrel.__cinit__.__psc__.append(clsrel)
        clsrel.__cfin__.__nsc__.append(clsrel)
       
    def link_objects(clsrel, objrel, oinit, ofin):
        assert isinstance(objrel, clsrel)
        objrel.__oinit__ = oinit
        objrel.__ofin__ = ofin
        objrel.__oinit__.__psc__.append(objrel)
        objrel.__ofin__.__nsc__.append(objrel)

    def unlink_objects(clsrel, objrel):
        assert isinstance(objrel, clsrel)
        objrel.__oinit__.__psc__.remove(objrel)
        objrel.__ofin__.__nsc__.remove(objrel)
        

def create_relation(cinit, name, cfin):
    meta = {'metaclass': Relation, }
    def update(clsdic):
        clsdic['__cinit__'] = cinit
        clsdic['__cfin__'] = cfin
    return types.new_class(name, kwds=meta, exec_body=update)
# Alias
Link = create_relation


PSC = Fonctor(lambda cls: getattr(cls, '__psc__', set()))
NSC = Fonctor(lambda cls: getattr(cls, '__nsc__', set()))

INIT = Fonctor(lambda rel: rel.__cinit__)
FIN = Fonctor(lambda rel: rel.__cfin__)

def opsc(obj, rel=None):
    if rel is None: return obj.__psc__
    return [r for r in obj.__psc__ if isinstance(r, rel)]
OPSC = Fonctor(opsc)
OPSCR = Fonctor(opsc)

def onsc(obj, rel=None):
    if rel is None: return obj.__nsc__
    return [r for r in obj.__nsc__ if isinstance(r, rel)]
ONSC = Fonctor(onsc)
ONSCR = Fonctor(onsc)


OINIT = Fonctor(lambda r: r.__oinit__)
OFIN = Fonctor(lambda r: r.__ofin__)


class Role:
# Role doit dériver de Att
# Faire un role qui retourne un objet et non une liste (fct de la card de R?)
# les rôles ne sont pas fournit à la complétion
    def __init__(self, relname):
        self.relname = relname
    def __get__(self, instance, owner_cls):
        rel = [r for r in owner_cls | PSC if r.__name__ == self.relname][0]
        # et si rel is None?
        return instance | OPSCR(rel) | OFIN


# Faire des relations ordered...et les foncteurs qui vont avec
# Optimiser les foncteurs pour éviter de tous parcourir si pas nécessaire



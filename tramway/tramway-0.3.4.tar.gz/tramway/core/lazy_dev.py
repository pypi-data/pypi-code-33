# -*- coding: utf-8 -*-

# Copyright © 2017-2018, Institut Pasteur
#   Contributor: François Laurent

# This file is part of the TRamWAy software available at
# "https://github.com/DecBayComp/TRamWAy" and is distributed under
# the terms of the CeCILL license as circulated at the following URL
# "http://www.cecill.info/licenses.en.html".

# The fact that you are presently reading this means that you have had
# knowledge of the CeCILL license and that you accept its terms.


import sys
from warnings import warn


def _ro_property_msg(property_name, related_attribute):
    if related_attributed:
        return '`{}` is a read-only property that reflects `{}`''s state'.format(property_name, related_attribute)
    else:
        return '`{}` is a read-only property'.format(property_name)

class PermissionError(AttributeError):
    def __init__(self, property_name, related_attribute):
        RuntimeError.__init__(self, property_name, related_attribute)

    def __str__(self):
        return _ro_property_msg(*self.args)

def ro_property_assert(obj, supplied_mutable, related_attribute=None, property_name=None, depth=0):
    if property_name is None:
        property_name = sys._getframe(depth + 1).f_code.co_name
    if supplied_mutable == getattr(obj, property_name):
        warn(_ro_property_msg(property_name, related_attribute), RuntimeWarning)
    else:
        raise PermissionError(property_name, related_attribute)


class LazyUnmodified(Exception):
    __slots__ = ('wrapped_exception',)
    def __init__(self, exc):
        self.wrapped_exception = exc
    def __repr__(self):
        return self.wrapped_exception.__repr__()
    def __str__(self):
        return self.wrapped_exception.__str__()

def lazy_binary(op, other):
    try:
        other = other.lazy_unwrap()
    except AttributeError:
        pass
    return op(other)

def lazy_inplace(self, op, other):
    try:
        other = other.lazy_unwrap()
    except AttributeError:
        pass
    self.lazy_signal(op, other)


class MutableLazy(object):
    """Wrapper for mutable lazy attributes.

    If any part of the attribute is modified, should signal the lazy container objects.
    """
    __slots__ = ('_listeners', '_mutable')
    def __init__(self, listener, value):
        self._listeners = list(listener)
        self._mutable = value
    def lazy_signal(self, method, *args, **kwargs):
        try:
            ret = method(*args, **kwargs)
        except:
            typ, exc, trace = sys.exc_info()
            try:
                exc = exc.wrapped_exception
            except:
                for listener_object, listener_attribute in self._listeners:
                    listener_object._lazy[listener_attribute] = False
            else:
                typ = type(exc)
            raise typ, exc, trace
        return ret
    def lazy_wrap(self, value):
        return check_mutable(value, self._listeners)
    def lazy_unwrap(self):
        return self._mutable
    def __del__(self):
        self.lazy_signal(self._mutable.__del__)
    def __repr__(self):
        return self._mutable.__repr__()
    def __str__(self):
        return self._mutable.__str__()
    def __bytes__(self):
        return self._mutable.__bytes__()
    def __format__(self, format_spec):
        return self._mutable.__format__(format_spec)
    def __lt__(self, other):
        return lazy_binary(self._mutable.__lt__, other)
    def __le__(self, other):
        return lazy_binary(self._mutable.__le__, other)
    def __eq__(self, other):
        return lazy_binary(self._mutable.__eq__, other)
    def __ne__(self, other):
        return lazy_binary(self._mutable.__ne__, other)
    def __gt__(self, other):
        return lazy_binary(self._mutable.__gt__, other)
    def __ge__(self, other):
        return lazy_binary(self._mutable.__ge__, other)
    def __hash__(self):
        return self._mutable.__hash__()
    def __bool__(self):
        return self._mutable.__bool__()
    def __getattr__(self, name):
        return self.lazy_wrap(self._mutable.__getattr__, name)
    def __getattribute__(self, name):
        return self.lazy_wrap(self._mutable.__getattribute__, name)
    def __setattr__(self, name, value):
        self.lazy_signal(self._mutable.__setattr__, name, value)
    def __delattr__(self, name):
        self.lazy_signal(self._mutable.__delattr__, name)
    def __dir__(self):
        return self._mutable.__dir__()
    def __get__(self, instance, owner):
        return self.lazy_wrap(self._mutable.__get__, instance, owner)
    def __set__(self, instance, value):
        self.lazy_signal(self._mutable.__set__, instance, value)
    def __delete__(self, instance):
        self.lazy_signal(self._mutable.__delete__, instance)
    def __set_name__(self, owner, name):
        self.lazy_signal(self._mutable.__set_name__, owner, name)
    #@property
    #def __slots__(self):
    #       return self._mutable.__slots__
    #@__slots__.setter
    #def __slots__(self, slots):
    #       signal = True
    #       try:
    #           self._mutable.__slots__ = slots
    #       except LazyUnmodified as e:
    #           raise e.wrapped_exception
    #       finally:
    #           if signal:
    #               self.lazy_signal()
    #@property
    #def __dict__(self):
    #       return self._mutable.__dict__
    #@__dict__.setter
    #def __dict__(self, fields):
    #       def _set():
    #           self._mutable.__dict__ = fields
    #       self.lazy_signal(_set)
    def __len__(self):
        return self._mutable.__len__()
    def __length_hint__(self):
        return self._mutable.__length_hint__()
    def __getitem__(self, key):
        return self.lazy_wrap(self._mutable.__getitem__(key))
    def __missing__(self, key):
        self.lazy_signal(self._mutable.__missing__, key)
    def __setitem__(self, key, value):
        self.lazy_signal(self._mutable.__setitem__, key, value)
    def __delitem__(self, key):
        self.lazy_signal(self._mutable.__delitem__, key)
    def __iter__(self):
        return self.lazy_wrap(self._mutable.__iter__())
    def __reversed__(self):
        return self.lazy_wrap(self._mutable.__reversed__())
    def __contains__(self, item):
        return self._mutable.__contains__(item)
    def __add__(self, other):
        return lazy_binary(self._mutable.__add__, other)
    def __sub__(self, other):
        return lazy_binary(self._mutable.__sub__, other)
    def __mul__(self, other):
        return lazy_binary(self._mutable.__mul__, other)
    def __matmul__(self, other):
        return lazy_binary(self._mutable.__matmul__, other)
    def __truediv__(self, other):
        return lazy_binary(self._mutable.__truediv__, other)
    def __floordiv__(self, other):
        return lazy_binary(self._mutable.__floordiv__, other)
    def __mod__(self, other):
        return lazy_binary(self._mutable.__mod__, other)
    def __divmod__(self, other):
        return lazy_binary(self._mutable.__divmod__, other)
    def __pow__(self, other):
        return lazy_binary(self._mutable.__pow__, other)
    def __lshift__(self, other):
        return lazy_binary(self._mutable.__lshift__, other)
    def __rshift__(self, other):
        return lazy_binary(self._mutable.__rshift__, other)
    def __and__(self, other):
        return lazy_binary(self._mutable.__and__, other)
    def __xor__(self, other):
        return lazy_binary(self._mutable.__xor__, other)
    def __or__(self, other):
        return lazy_binary(self._mutable.__or__, other)
    def __radd__(self, other):
        return lazy_binary(self._mutable.__radd__, other)
    def __rsub__(self, other):
        return lazy_binary(self._mutable.__rsub__, other)
    def __rmul__(self, other):
        return lazy_binary(self._mutable.__rmul__, other)
    def __rmatmul__(self, other):
        return lazy_binary(self._mutable.__rmatmul__, other)
    def __rtruediv__(self, other):
        return lazy_binary(self._mutable.__rtruediv__, other)
    def __rfloordiv__(self, other):
        return lazy_binary(self._mutable.__rfloordiv__, other)
    def __rmod__(self, other):
        return lazy_binary(self._mutable.__rmod__, other)
    def __rdivmod__(self, other):
        return lazy_binary(self._mutable.__rdivmod__, other)
    def __rpow__(self, other):
        return lazy_binary(self._mutable.__rpow__, other)
    def __rlshift__(self, other):
        return lazy_binary(self._mutable.__rlshift__, other)
    def __rrshift__(self, other):
        return lazy_binary(self._mutable.__rrshift__, other)
    def __rand__(self, other):
        return lazy_binary(self._mutable.__rand__, other)
    def __rxor__(self, other):
        return lazy_binary(self._mutable.__rxor__, other)
    def __ror__(self, other):
        return lazy_binary(self._mutable.__ror__, other)
    def __iadd__(self, other):
        lazy_inplace(self, self._mutable.__iadd__, other)
    def __isub__(self, other):
        lazy_inplace(self, self._mutable.__isub__, other)
    def __imul__(self, other):
        lazy_inplace(self, self._mutable.__imul__, other)
    def __imatmul__(self, other):
        lazy_inplace(self, self._mutable.__imatmul__, other)
    def __itruediv__(self, other):
        lazy_inplace(self, self._mutable.__itruediv__, other)
    def __ifloordiv__(self, other):
        lazy_inplace(self, self._mutable.__ifloordiv__, other)
    def __imod__(self, other):
        lazy_inplace(self, self._mutable.__imod__, other)
    def __idivmod__(self, other):
        lazy_inplace(self, self._mutable.__idivmod__, other)
    def __ipow__(self, other):
        lazy_inplace(self, self._mutable.__ipow__, other)
    def __ilshift__(self, other):
        lazy_inplace(self, self._mutable.__ilshift__, other)
    def __irshift__(self, other):
        lazy_inplace(self, self._mutable.__irshift__, other)
    def __iand__(self, other):
        lazy_inplace(self, self._mutable.__iand__, other)
    def __ixor__(self, other):
        lazy_inplace(self, self._mutable.__ixor__, other)
    def __ior__(self, other):
        lazy_inplace(self, self._mutable.__ior__, other)
    def __neg__(self):
        return self.lazy_wrap(self._mutable.__neg__())
    def __pos__(self):
        return self.lazy_wrap(self._mutable.__pos__())
    def __abs__(self):
        return self.lazy_wrap(self._mutable.__abs__())
    def __invert__(self):
        return self.lazy_wrap(self._mutable.__invert__())
    def __complex__(self):
        return self._mutable.__complex__()
    def __int__(self):
        return self._mutable.__int__()
    def __float__(self):
        return self._mutable.__float__()
    def __index__(self):
        return self.lazy_wrap(self._mutable.__index__())
    def __round__(self):
        return self.lazy_wrap(self._mutable.__round__())
    def __trunc__(self):
        return self.lazy_wrap(self._mutable.__trunc__())
    def __floor__(self):
        return self.lazy_wrap(self._mutable.__floor__())
    def __ceil__(self):
        return self.lazy_wrap(self._mutable.__ceil__())
    def __enter__(self):
        return self.lazy_signal(self._mutable.__enter__)
    def __exit__(self, exc_type, exc_value, traceback):
        self.lazy_signal(self._mutable.__exit__, exc_type, exc_value, traceback)


def check_mutable(obj, listeners=None):
    if obj is None or isinstance(obj, (type, bool, int, float, complex, bytes, str, tuple, slice, frozenset)) or callable(obj):
        return obj
    else:
        if listeners is None:
            raise ValueError('argument `listeners` is required')
        try:
            value._mutable
            listeners = listeners + value._listeners
        except:
            pass
        return MutableLazy(listeners, obj)


class Lazy(object):
    """Lazy store.

    Lazily computes and stores attributes through properties, so that the stored attributes can be
    (explicitly) deleted anytime to save memory.

    The :attr:`__lazy__` static attribute is a list of the properties that implement such a 
    mechanism.

    Per default each lazy property ``name`` manages a private ``_name`` attribute. 
    This naming convention can be overwritten by heriting `Lazy` and overloading 
    :meth:`__tolazy__` and :meth:`__fromlazy__` methods.

    An unset lazy attribute/property always has value ``None``.

    A getter will typically look like this:

    .. code-block:: python

        @property
        def name(self):
            if self._name is None:
                self._name = # add some logics
            return self.__lazyreturn__(self._name)

    A fully functional setter will typically look like this:

    .. code-block:: python

        @name.setter
        def name(self, value):
            self.__lazysetter__(value)

    A read-only lazy property will usually look like this:

    .. code-block:: python

        @name.setter
        def name(self, value):
            self.__lazyassert__(value)

    `__lazyassert__` can unset ``_name`` (set it to ``None``) but any other value is treated as 
    illegal. `__lazyassert__` compares ``value`` with ``self.name`` and raises a warning if the
    values equal to each other, or throws an exception otherwise.

    """
    __slots__ = ('_lazy',)

    __lazy__  = ()

    def __init__(self):
        self._lazy = {name: True for name in self.__lazy__}
        for name in self.__lazy__:
            setattr(self, self.__fromlazy__(name), None)

    def __returnlazy__(self, name, value):
        return check_mutable(value, [(self, name)])

    def __lazyreturn__(self, value, depth=0):
        caller = sys._getframe(depth + 1).f_code.co_name
        return self.__returnlazy__(caller, value)

    def __tolazy__(self, name):
        """Returns the property name that corresponds to an attribute name."""
        return name[1:]

    def __fromlazy__(self, name):
        """Returns the attribute name that corresponds to a property name."""
        return '_{}'.format(name)

    def __setlazy__(self, name, value):
        """Sets property `name` to `value`."""
        self._lazy[name] = value is None
        try:
            value = value.lazy_unwrap()
        except AttributeError:
            pass
        setattr(self, self.__fromlazy__(name), value)

    def __lazysetter__(self, value, depth=0):
        """Sets the property which name is the name of the caller."""
        caller = sys._getframe(depth + 1).f_code.co_name
        self.__setlazy__(caller, value)

    def __lazyassert__(self, value, related_attribute=None, name=None, depth=0):
        if value is None: # None has a special meaning for lazy attributes/properties
            if name is None:
                self.__lazysetter__(value, depth + 1)
            else:
                self.__setlazy__(name, value)
        else:
            ro_property_assert(self, value, related_attribute, name, depth + 1)

    def unload(self, visited=None):
        """
        Recursively clear the lazy attributes.

        Beware: only direct Lazy object attributes are unloaded, 
            not Lazy objects stored in non-lazy attributes!

        *Deprecated*
        """
        warn('`unload` will be removed soon', DeprecationWarning)
        if visited is None:
            visited = set()
        elif id(self) in visited:
            # already unloaded
            return
        visited.add(id(self))
        try:
            names = self.__slots__
        except:
            names = self.__dict__
        standard_attrs = []
        # set lazy attributes to None (unset them so that memory is freed)
        for name in names:
            if self._lazy.get(self.__tolazy__(name), False):
                try:
                    setattr(self, name, None)
                except AttributeError:
                    pass
            else:
                standard_attrs.append(name)
        # search for Lazy object attributes so that they can be unloaded
        for name in standard_attrs: # standard or overwritten lazy
            try:
                attr = getattr(self, name)
            except AttributeError:
                pass
            if isinstance(attr, Lazy):
                attr.unload(visited)



def lightcopy(x):
    """
    Return a copy and call `unload` if available.

    Arguments:

        x (any): object to be copied and unloaded.

    Returns:

        any: copy of `x`.

    *Deprecated*
    """
    warn('`lightcopy` will be removed soon', DeprecationWarning)
    return x


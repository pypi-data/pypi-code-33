#------------------------------------------------------------------------
#
# Copyright (c) Microsoft Corporation.  All rights reserved.
#
# Extensions to inspect
#
#------------------------------------------------------------------------
"""
    Module that contains inpection functions.
"""
import sys
import inspect
from . import (
    verify,
    string_exceptions,
    exception
)

def is_callable(obj):
    """
        Returns true if obj is a callable
    """
    return hasattr(obj, "__call__")

def is_iterable(obj):
    """
        Returns true if obj is iterable
    """
    return hasattr(obj, "__next__")

def get_class(modulename, classname, caseinsensitive=False):
    """
        Given a module name and class name, return the class object, if any

    """
    verify.not_none_or_empty(modulename, "modulename")
    verify.not_none_or_empty(modulename, "classname")

    moduleobj = sys.modules[modulename]
    classtype = None
    if caseinsensitive:
        matches = inspect.getmembers(moduleobj,
                                     lambda cls: inspect.isclass(cls) and
                                                 string_exceptions.equals_caseinsensitive(cls.__name__, classname))
        if matches:
            classtype = matches[0][1]
    else:
        classtype = getattr(moduleobj, classname, None)
    return classtype

def create_instance(modulename, classname, case_insensitive, *args):
    """
        Given a modulename and classname, create an instance of the class
        Throws if the class was not resolved.

    """
    classtype = get_class(modulename, classname, case_insensitive)
    if classtype:
        return classtype(*args)
    raise NameError(modulename + "." + classname)

def get_private(obj, valuename):
    """
        Returns a private value from the object
    """
    #
    # Python mangles names of private variables in a predictable way:
    # https://docs.python.org/3.5/tutorial/classes.html#tut-private
    #
    verify.not_none(obj, "obj")
    verify.not_none_or_empty(valuename, "valuename")
    verify.true(valuename.startswith("__"), "valuename")

    objclass = obj.__class__
    if not objclass:
        raise exception.NotSupportedException("obj is not a class instance")
    compiled_name = "_" + objclass.__name__ + valuename
    return getattr(obj, compiled_name)

def get_protected(obj, valuename):
    """
        Returns a protected value from the object

    """
    #
    # Python mangles names of private variables in a predictable way:
    # https://docs.python.org/3.5/tutorial/classes.html#tut-private
    #
    verify.not_none(obj, "obj")
    verify.not_none_or_empty(valuename, "valuename")
    verify.true(valuename.startswith("_"), "valuename")

    objclass = obj.__class__
    if not objclass:
        raise exception.NotSupportedException("obj is not a class instance")
    return getattr(obj, valuename)

def call_privatemethod(obj, methodname, *args):
    """
        Given the name of a private method, calls it with the given args

        :param methodname: str
            E.g. __my_method

    """
    return get_private(obj, methodname)(*args)

def call_protectedmethod(obj, methodname, *args):
    """
        Given the name of a protected method, calls it with the given args

        :param methodname: str
            E.g. __my_method

    """
    return get_protected(obj, methodname)(*args)

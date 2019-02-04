import sys
import traceback

from collections import Iterable
from functools import wraps

from python_openapi3.logger import log
from python_openapi3.pycompat23_local import basestr, OASMetaBase

DEFAULT = object()
DEFAULT_IGNORE=object()

def ensure_allowed(kwargs,allowed_keys,msg="Unknown KWARGS Present: {violating_keys}\n\nALLOWED KWARGS:{allowed_values}"):
    disallowed_keys = set(kwargs.keys()).difference(allowed_keys)
    if disallowed_keys:
        fmtVars = {
            "violating_keys": ", ".join(disallowed_keys),
            "allowed_values": ", ".join(allowed_keys)
        }
        raise TypeError(msg.format(**fmtVars))
def assert_class(p, classObType):
    if not isinstance(p,classObType):
        msg = "Unexpeceted {classname}: Expected {classname} not {p!r}"
        raise TypeError(msg.format(classname=classObType, p=p))

def ensure_class(p, classObType,
                 msg= "Unexpeceted {classname}: Expected {classname} or a dict: not {p!r}"):
    """
     forces a value to cast to the specified type
    >>> ensure_class("7",int)
    7
    >>> ensure_class((("a",6),("b",8)),dict)
    {'a': 6, 'b': 8}
    >>> class Demo:
    ...     def __init__(self,a,b,c):
    ...         pass
    >>> ensure_class({'a':3,'b':4,'c':'hello'},Demo) # doctest:+ELLIPSIS
    <_util.Demo instance at 0x...>

    :param p:
    :param classOb:
    :return:
    """
    if isinstance(p, classObType):
        return p
    try:
        return classObType(p)
    except Exception as e:
        errors = [sys.exc_info()]
        if isinstance(p,dict):
            try:
                return classObType(**p)
            except Exception as ed:
                errors.append(sys.exc_info())

        elif isinstance(p,Iterable):
            try:
                return classObType(*p)
            except Exception as el:
                errors.append(sys.exc_info())
    if hasattr(classObType,"typeMessage"):
        msg = classObType.typeMessage
    log.error("TYPING ERROR:",exc_info=errors[-1])
    raise TypeError(msg.format(classname=classObType.__name__, p=p))









def guess_example_from_schema(schema):
    """
    >>> s = {"type":"string"}
    >>> guess_example_from_schema(s)
    'a string'
    >>> s.update({"type":"number"})
    >>> guess_example_from_schema(s)
    0.0
    >>> s.update({"type":"object","properties":{"cat_url":{"type":"string","example":"http://www..."}}})
    >>> guess_example_from_schema(s)
    {'cat_url': 'http://www...'}
    >>> guess_example_from_schema({"type":"array","items":{"type":"string"}})
    ['a string']

    :param schema:
    :return:
    """
    if isinstance(schema,basestr):
        return schema
    if not isinstance(schema,dict) and isinstance(schema,Iterable):
        result = [guess_example_from_schema(s) for s in schema]
        return result
    try:
        if schema.get('example',None) is not None:
            return schema['example']
    except:
        traceback.print_exc()
        pass
    example = {
        "string":"a string",
        "number":0.0,
        "integer":0,
    }.get(schema['type'],None)
    if example is not None:
        return example
    if schema['type'] == "array":
        return guess_example_from_schema(schema['items'])
    elif schema['type'] == "object":
        return {propName:guess_example_from_schema(propVal) for propName,propVal in schema.get('properties',{}).items()}

class OASBase(OASMetaBase):
    """
    this class should be subclassed by all OAS elements, and not directly invoked
    subclasses may overload `preprocess_kwargs` as a classmethod to hook into any kwargs
    passed in before they are passed to __init__
    """

    types={}
    enums={}
    allowed_kwargs=None

    def update(self,kwargs,ignored=None):
        if not self._data:
            self._data = {}
        ignored_set = set(['cls','self','kwargs','args'])
        if ignored:
            ignored_set = ignored_set.union(ignored)
        for k,v in kwargs.items():
            if k in ignored_set:
                continue
            if v is DEFAULT_IGNORE:
                continue
            setattr(self,k,v)
    def __setattr__(self, key, value):
        if key in dir(self):
            self.__dict__[key] = value
            return
        classname = self.__class__.__name__
        if self.allowed_kwargs and key not in self.allowed_kwargs:
            raise TypeError("Argument %s is not allowed for type %s"%(key,classname))
        allowed_values = self.enums.get(key, [value, ])
        if value not in allowed_values:
            raise ValueError("%s - Invalid Value For Parameter %s, got %r, but expected %s"%(classname, key, value, allowed_values))

        value = ensure_class(value,self.types.get(key,type(value)))
        self._data[key] = value



class OASTypedSchemaList(OASBase):
    """
    presents a class that ensures a unified list type

    >>> class IntList(OASTypedSchemaList):
    ...     schemaType = int
    >>> ensure_class([1,"2",3.4,5.9],IntList)
    <IntList - [1, 2, 3, 5]>
    >>> ensure_class([1,"2",3.4,"5.9"],IntList)
    TypeError: Unexpeceted IntList: Expected IntList or a list of integers: not [1, '2', 3.4, '5.9']

    """
    schemaType=str
    _data = []
    typeMessage = "Unexpeceted {classname}: Expected {classname} or a list of integers: not {p!r}"
    def __init__(self,initial_list=None):
        if initial_list:
            self.extend(initial_list)
    def __getitem__(self, item):
        return self._data[item]
    def __setitem__(self, key, value):
        self._data[key] = ensure_class(value,self.schemaType,self.typeMessage)
    def __getattr__(self, item):
        return getattr(self._data,item)
    def append(self,value):
        self._data.append(ensure_class(value,self.schemaType,self.typeMessage))
    def extend(self,values):
        if not self._data:
            self._data = []
        values = [ensure_class(value, self.schemaType,self.typeMessage) for value in values]
        self._data.extend(values)
    def to_dict(self):
        return [getattr(v,'to_dict',lambda:v)() for v in self._data]
    def __iter__(self):
        return iter(self._data)
def TypedListFactory(T):
    """
    Provides a simpler way to provide a
    OASTypedSchemaList

    >>> ensure_class(['1','2',3.4,4,5],TypedListFactory(int))
    <OASTypedList - [1, 2, 3, 4, 5]>

    :param T: the <Type> to cast all list values for
    :return: a new class of the specified type
    """
    class OASTypedList(OASTypedSchemaList):
        __name__ = "O"
        schemaType = T
    return OASTypedList

class OASTypedSchemaMap(OASBase):
    """
    Like The OASTypedSchemaList, this attempts to provide an
    interface to a unified value type in the dict,
    this does not attempt to enforce the keys of the dict

    >>> class IntDict(OASTypedSchemaMap):
    ...    schemaType=int
    >>> IntDict({'x':'5','y':7.8,'z':'8'})
    <IntDict - {'y': 7, 'x': 5, 'z': 8}>


    """
    schemaType = str
    def __init__(self,initial_map=None):
        if initial_map:
            self.update(initial_map)

    def __setattr__(self, key, value):
        self.types[key]=self.schemaType
        OASBase.__setattr__(self,key,value)
    def __getattr__(self, item):
        return getattr(self._data,item)

def TypedMapFactory(T):
    """
    attempts to provide easier instantiation of our Typed map class

    >>> TypedMapFactory(int)({'x':'5','y':7.8,'z':'8'})
    <OASTypedSchemaMap - {'y': '7.8', 'x': '5', 'z': '8'}>

    :param T: the type to map all values to
    :return:
    """
    class OASTypedMap(OASTypedSchemaMap):
        schemaType = T
    return OASTypedMap


class UnionType(OASBase):
    _classtypes = int,float
    value = None
    _type = None

    def __init__(self,value):
        for classType in self._classtypes:
            try:
                self.value = ensure_class(value,classType)
            except Exception as e:
                # traceback.print_exc()
                self._type = classType
                continue
            else:
                # wraps(self.value)(self)
                return
        raise TypeError("Unable To Cast: %r to any of %s"%(value,self._classtypes))
    def __getattr__(self, item):
        # if item in dir(self):
        #     return self.__dict__[item]
        return getattr(self.value,item)
    def __setattr__(self, key, value):
        if key in dir(self):
            self.__dict__[key] = value
        else:
            setattr(self.value,key,value)
    def __getitem__(self, item):
        return self.value[item]
    def __setitem__(self, key, value):
        self.value[key] = value
    def __str__(self):
        return str(self.value)

def UnionTypeFactory(*classTypes):
    """
    create UnionTypes

    >>> UnionTypeFactory(int,float)("2.3")
    <MyUnionClass - 2.3>

    :param classTypes: a list of classTypes to try and cast our value to
    :return:
    """
    class MyUnionClass(UnionType):
        _classtypes = classTypes
    return MyUnionClass
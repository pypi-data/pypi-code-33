from collections import Iterable
from past.builtins import basestring as basestr

class _Dictified(object):
    """
    this allows a class to provide most of the interface of a traditional dict

    also provides a to_dict method that recursively tries to ensure serializeable data

    >>> class X(_Dictified):
    ...    def __init__(self,**kwargs):
    ...        self._data = kwargs
    >>> X(a=5,b7=2).to_dict()
    {'a': 5, 'b7': 2}

    """

    _data = {}
    def __init__(self,*args,**kwargs):
        pass
    @classmethod
    def from_dict(cls,dict):
        return cls(**dict)
    def __getattr__(self, item):
        try:
            return self._data[item]
        except:
            return getattr(self._data,item)
    def __getitem__(self, item):
        return getattr(self,item)
    def __setattr__(self, key, value):
        self._data[key] = value
    def __setitem__(self, key, value):
        setattr(self,key,value)
    def __eq__(self, other):
        if hasattr(other, "to_dict"):
            return self.to_dict() == other.to_dict()
        elif isinstance(other, dict):
            return self.to_dict() == other
    def __repr__(self):
        return "<%s - %s>"%(self.__class__.__name__,self)
    def __str__(self):
        return str(self._data)
    def __contains__(self, item):
        return item in self._data

    def to_dict(self):
        def convert_list(L):
            result = []
            for itm in L:
                if hasattr(itm,'to_dict'):
                    itm = itm.to_dict()
                elif isinstance(itm,(int,basestr)):
                    itm = itm
                elif isinstance(itm,Iterable):
                    itm = convert_list(itm)
                elif isinstance(itm,dict):
                    itm = convert_dict(itm)
                result.append(itm)
            return result
        def convert_dict(D):
            result = {}
            for key, value in D.items():
                if hasattr(value,'to_dict'):
                    value = value.to_dict()
                elif isinstance(value,(int,basestr)):
                    value = value
                elif isinstance(value, dict):
                    value = convert_dict(value)
                elif isinstance(value,Iterable):
                    value = convert_list(value)

                result[key] = value
            return result
        if isinstance(self._data,dict):
            return convert_dict(self._data)
        elif isinstance(self._data,Iterable):
            return convert_list(self._data)

class oas__metaclass__(type):
    def __call__(self, *args, **kwargs):
        #: allow classes to overload preprocess_args_kwargs
        args, kwargs = getattr(self, 'preprocess_args_kwargs', lambda a, kw: (a, kw))(args, kwargs)
        #: allow classes to overload preprocess_args
        args = getattr(self, 'preprocess_args', lambda a: a)(args)
        #: allow classes to overload preprocess_kwargs
        kwargs = getattr(self, 'preprocess_kwargs', lambda kw: kw)(kwargs)
        return type.__call__(self, *args, **kwargs)

import functools

import attr
import multipledispatch


class reify(object):
    """ Use as a class method decorator.  It operates almost exactly like the
    Python ``@property`` decorator, but it puts the result of the method it
    decorates into the instance dict after the first call, effectively
    replacing the function it decorates with an instance variable.  It is, in
    Python parlance, a non-data descriptor.  The following is an example and
    its usage:
    .. doctest::
        >>> from pyramid.decorator import reify
        >>> class Foo(object):
        ...     @reify
        ...     def jammy(self):
        ...         print('jammy called')
        ...         return 1
        >>> f = Foo()
        >>> v = f.jammy
        jammy called
        >>> print(v)
        1
        >>> f.jammy
        1
        >>> # jammy func not called the second time; it replaced itself with 1
        >>> # Note: reassignment is possible
        >>> f.jammy = 2
        >>> f.jammy
        2
    """

    def __init__(self, wrapped):
        self.wrapped = wrapped
        functools.update_wrapper(self, wrapped)

    def __get__(self, inst, objtype=None):
        if inst is None:
            return self
        val = self.wrapped(inst)
        setattr(inst, self.wrapped.__name__, val)
        return val


@attr.s
class ExtensibleDispatcher:

    dispatcher = attr.ib(factory=lambda: multipledispatch.Dispatcher("dispatcher"))
    _name_to_codec = attr.ib(factory=dict)

    def register(self, *args, **kwargs):
        # names = tuple(cls.__name__ for cls in args)
        # self._name_to_codec[names] = self.dispatcher.funcs[names]
        return self.dispatcher.register(*args, **kwargs)

    def add(self, *args, **kwargs):
        return self.dispatcher.add(*args, **kwargs)

    def __call__(self, *args, **kwargs):
        return self.dispatcher(*args, **kwargs)

    def copy(self):
        dispatcher = type(self.dispatcher)(
            name=self.dispatcher.name, doc=self.dispatcher.doc
        )
        dispatcher.funcs = self.dispatcher.funcs.copy()
        return type(self)(dispatcher)

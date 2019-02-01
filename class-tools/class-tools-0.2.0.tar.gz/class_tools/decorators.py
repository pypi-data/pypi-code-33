# system modules
import textwrap
import warnings
import functools
import types
import itertools
import inspect
import re
from abc import abstractproperty

# internal modules
from class_tools.utils import *

# external modules


class NotSet:
    """
    Class to indicate that an argument has not been specified.
    """

    pass


def conflicting_arguments(*conflicts):
    """
    Create a decorator which raises a :any:`ValueError` when the decorated
    function was called with conflicting arguments. Works for both positional
    and keyword arguments.

    Args:
        conflicts (sequence of str): the arguments which should not be
            specified together.

    Returns:
        callable: a decorator for callables
    """

    def decorator(decorated_fun):
        @functools.wraps(decorated_fun)
        def wrapper(*args, **kwargs):
            spec = inspect.getfullargspec(decorated_fun)
            posargs = dict(
                zip(itertools.chain(spec.args, spec.kwonlyargs), args)
            )
            arguments = set(kwargs).union(set(posargs))
            if arguments and all(map(arguments.__contains__, conflicts)):
                raise ValueError(
                    "function {fun} called with "
                    "conflicting arguments: {args}".format(
                        fun=repr(decorated_fun.__name__),
                        args=", ".join(map(repr, conflicts)),
                    )
                )

            return decorated_fun(*args, **kwargs)

        return wrapper

    return decorator


def classdecorator(decorated_fun):
    """
    Decorator for other decorator functions that are supposed to only be
    applied to classes.

    Raises:
        ValueError : if the resulting decorator is applied to non-classes
    """

    @functools.wraps(decorated_fun)
    def wrapper(decorated_cls):
        if not isinstance(decorated_cls, type):
            raise TypeError(
                (
                    "{cls} object is not a type and "
                    "cannot be decorated with this decorator"
                ).format(cls=repr(type(decorated_cls).__name__))
            )
        return decorated_fun(decorated_cls)

    return wrapper


def add_property(name, *args, abstract=False, **kwargs):
    """
    Create a :any:`classdecorator` that adds a :any:`property` or
    :any:`abc.abstractproperty` to the decorated class.

    Args:
        name (str): the name for the property
        abstract (bool, optional): whether to create an :any:`abstractproperty`
            instead of a :any:`property`
        args, kwargs: arguments passed to :any:`property` (or
            :any:`abstractproperty` of `abstract=True`)

    Returns:
        :any:`classdecorator` : decorator for classes
    """

    @classdecorator
    def decorator(decorated_cls):
        prop = (abstractproperty if abstract else property)(*args, **kwargs)
        setattr(decorated_cls, name, prop)
        return decorated_cls

    return decorator


def readonly_property(name, getter, *args, **kwargs):
    """
    Create a :any:`classdecorator` that adds a read-only :any:`property` (i.e.
    without setter and deleter).

    Args:
        name (str): the name for the constant
        getter (callable): the :any:`property.getter` to use
        args, kwargs: arguments passed to :any:`add_property`
    """
    return functools.partial(add_property, name, fget=getter)(*args, **kwargs)


def constant(name, value, *args, **kwargs):
    """
    Create a :any:`classdecorator` that adds a :any:`readonly_property`
    returning a static value to the decorated class.

    Args:
        name (str): the name for the constant
        value (object): the value of the constant
        args, kwargs: arguments passed to :any:`readonly_property`
    """
    return functools.partial(readonly_property, name, getter=lambda s: value)(
        *args, **kwargs
    )


@conflicting_arguments("static_default", "dynamic_default")
@conflicting_arguments("static_type", "dynamic_type")
def wrapper_property(
    name,
    *args,
    attr=NotSet,
    static_default=NotSet,
    dynamic_default=NotSet,
    set_default=False,
    static_type=NotSet,
    dynamic_type=NotSet,
    doc_default=None,
    doc_type=None,
    doc_getter=None,
    doc_setter=None,
    doc_property=None,
    **kwargs
):
    """
    Create a :any:`classdecorator` that adds a :any:`property` with getter,
    setter and deleter, wrapping an attribute.

    Args:
        name (str): the name for the constant
        attr (str, optional): the name for the wrapped attribute. If unset,
            use ``name`` with an underscore (``_``) prepended.
        static_default (object, optional): value to use in the getter if the
            ``attr`` is not yet set
        dynamic_default (object, optional): the return value of this function
            (called with the object as argument) is used in the getter if the
            ``attr`` is not yet set.
        set_default (bool, optional): whether to set the ``attr`` to the
            ``static_default`` or ``dynamic_default`` (if specified) in the
            getter when it was not yet set. Default is ``False``.
        doc_default, doc_type, doc_getter, doc_setter (str, optional):
            documentation strings.
        static_type (callable, optional): function to convert the value in the
            setter.
        dynamic_type (callable, optional): function to convert the value in the
            setter. Differing from ``static_type``, this function is also
            handed the object reference as first argument.
        args, kwargs: arguments passed to :any:`add_property`
    """
    # determine the attribute
    if attr is NotSet:
        attr = "".join(("_", name))
    # determine the getter
    doc_getter_default = None
    if static_default is not NotSet:
        if set_default:

            def getter(self):
                try:
                    return getattr(self, attr)
                except AttributeError:
                    setattr(self, attr, static_default)
                return getattr(self, attr)

        else:

            def getter(self):
                return getattr(self, attr, static_default)

        doc_getter_default = "``{}``".format(repr(static_default))

    elif dynamic_default is not NotSet:
        try:
            s = inspect.getfullargspec(dynamic_default)
            assert len(s.args) == 1 and not any(
                getattr(s, a)
                for a in (
                    "varargs",
                    "varkw",
                    "defaults",
                    "kwonlyargs",
                    "kwonlydefaults",
                )
            ), "needs to take exactly one positional argument"
        except BaseException as e:  # pragma: no cover
            raise ValueError(
                "dynamic_default needs to be "
                "usable as a method: {}".format(e)
            )
        if set_default:

            def getter(self):
                try:
                    return getattr(self, attr)
                except AttributeError:
                    setattr(self, attr, dynamic_default(self))
                return getattr(self, attr)

        else:

            def getter(self):
                try:
                    return getattr(self, attr)
                except AttributeError:
                    return dynamic_default(self)

        doc_getter_default = "the return value of {}".format(
            "a user-specified function"
            if (isinstance(dynamic_default, types.LambdaType))
            else "``{}``".format(dynamic_default.__name__)
        )

    else:  # no default

        def getter(self):
            return getattr(self, attr)

    doc_getter = doc_getter or (
        "Return the value of the ``{attr}`` attribute. "
        + (
            (
                "If it hasn't been set yet, "
                "it will be set to the default: {default}"
            )
            if (doc_getter_default and set_default)
            else ""
        )
    ).format(attr=attr, default=doc_getter_default)

    # determine the setter
    doc_setter_type = None
    if static_type is not NotSet:

        def setter(self, new):
            setattr(self, attr, static_type(new))

        doc_setter_type = "new values are modified with {}".format(
            "a user-specified function"
            if (isinstance(static_type, types.LambdaType))
            else "``{}``".format(static_type.__name__)
        )

    elif dynamic_type is not NotSet:
        try:
            s = inspect.getfullargspec(dynamic_type)
            assert len(s.args) == 2 and not any(
                getattr(s, a)
                for a in (
                    "varargs",
                    "varkw",
                    "defaults",
                    "kwonlyargs",
                    "kwonlydefaults",
                )
            ), "needs to take exactly two positional argument"
        except BaseException as e:  # pragma: no cover
            raise ValueError(
                "dynamic_type needs to be " "usable as a method: {}".format(e)
            )

        def setter(self, new):
            setattr(self, attr, dynamic_type(self, new))

        doc_setter_type = "new values are modified with {}".format(
            "a user-specified function"
            if (isinstance(dynamic_type, types.LambdaType))
            else "``{}``".format(dynamic_type.__name__)
        )

    else:  # no type

        def setter(self, new):
            setattr(self, attr, new)

    doc_setter = doc_setter or ("Set the ``{attr}`` attribute").format(
        attr=attr
    )
    doc_type = doc_type or doc_setter_type

    # create the docstring
    docstring = "\n\n".join(
        filter(
            bool,
            (
                "{doc_property}",
                ":type: {doc_type}" if doc_type else "",
                ":getter: {doc_getter}" if doc_getter else "",
                ":setter: {doc_setter}" if doc_setter else "",
            ),
        )
    ).format(
        doc_property=doc_property or ("{} property").format(name),
        doc_type=doc_type or doc_setter_type or ":any:`object`",
        doc_getter=doc_getter or "return the property's value",
        doc_setter=doc_setter or "set the property's value",
    )

    return functools.partial(
        add_property,
        name,
        fget=getter,
        fset=setter,
        fdel=lambda s: (delattr(s, attr) if hasattr(s, attr) else None),
        doc=docstring,
    )(*args, **kwargs)


def with_init_from_properties():
    """
    Create a :any:`classdecorator` that **overwrites** the ``__init__``-method
    so that it accepts arguments according to its read- and settable
    properties.

    Returns:
        callable : :any:`classdecorator`
    """

    @classdecorator
    def decorator(decorated_cls):
        def __init__(self, **properties):
            cls = type(self)
            for name, prop in get_properties(
                cls, getter=True, setter=True
            ).items():
                if name in properties:
                    setattr(self, name, properties.pop(name))
            for arg, val in properties.items():
                warnings.warn(
                    (
                        "{cls}.__init__() got an "
                        "unexpected keyword argument {arg}"
                    ).format(cls=cls.__name__, arg=repr(arg))
                )

        setattr(decorated_cls, "__init__", __init__)

        return decorated_cls

    return decorator


def with_repr_like_init_from_properties(indent=" " * 4, full_path=False):
    """
    Create a :any:`classdecorator` that **overwrites** the ``__repr__``-method
    so that it returns a representation according to the decorated class'
    properties.

    .. note::

        The created ``__repr__``-method assumes that the decorated class'
        ``__init__``-method accepts keyword arguments similar to its
        properties. The :any:`with_init_from_properties` :any:`classdecorator`
        creates such an initializer.

    Args:
        indent(str, optional): the indentation string. The default is four
            spaces.
        full_path (bool, optional): whether to use the :any:`full_object_path`
            instead of just the object names. Defaults to ``False``.

    Returns:
        callable : :any:`classdecorator`
    """

    @classdecorator
    def decorator(decorated_cls):
        def __repr__(self):
            cls = type(self)
            clspath = (
                full_object_path(type(self))
                if full_path
                else type(self).__name__
            )

            properties = get_properties(cls, getter=True, setter=True)

            # create "prop = {prop}" string tuple for reprformat
            props_kv = tuple(
                map(
                    functools.partial(textwrap.indent, prefix=indent),
                    map(
                        lambda pv: "{p}={v}".format(
                            p=pv[0],
                            v=re.sub(
                                "\n", indent + "\n", repr(pv[1].fget(self))
                            ),
                        ),
                        sorted(properties.items()),
                    ),
                )
            )

            # create the format string
            reprformatstr = "{____cls}({args})".format(
                ____cls=clspath,
                args=("\n{}\n" if props_kv else "{}").format(
                    ",\n".join(props_kv)
                ),
            )

            return reprformatstr.format(
                **{
                    name: repr(prop.fget(self))
                    for name, prop in properties.items()
                }
            )

        setattr(decorated_cls, "__repr__", __repr__)

        return decorated_cls

    return decorator


def with_eq_comparing_properties():
    """
    Create a :any:`classdecorator` that **overwrites** the ``__eq__``-method so
    that it compares all properties with a getter for equality.

    Returns:
        callable : :any:`classdecorator`
    """

    @classdecorator
    def decorator(decorated_cls):
        def __eq__(self, other):
            other_properties = get_properties(other, getter=True)
            for name, prop in get_properties(self, getter=True).items():
                if name not in other_properties:
                    raise TypeError(
                        (
                            "{other_cls} object has no property "
                            "{property} and thus cannot be compared to "
                            "{our_cls} object"
                        ).format(
                            other_cls=repr(type(other).__name__),
                            property=repr(name),
                            our_cls=repr(type(self).__name__),
                        )
                    )
                if prop.fget(self) != other_properties.get(name).fget(other):
                    return False
            return True

        __eq__.__doc__ = (
            "Checks whether all properties of "
            "this object match the corresponding "
            "properties of the given object to compare"
        )
        setattr(decorated_cls, "__eq__", __eq__)

        return decorated_cls

    return decorator

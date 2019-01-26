# system modules
import textwrap
import warnings
import functools
import re

# internal modules
from class_tools.utils import *

# external modules


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


def has_property(
    name,
    type=None,
    type_doc=None,
    default=lambda: None,
    set_default=True,
    prefix="_",
    doc=None,
):
    """
    Create a :any:`classdecorator` that adds a property with getter, setter and
    deleter to a class, wrapping around an attribute.

    Args:
        name (str): the name of the property
        type (callable, optional): method to transform given values in the
            setter with. The default is to just pass the given value.
        type_doc (str, optional): the documentation of the property's type
        default (callable, optional): Callable returning the default value
            for the property.  The default just returns ``None``.
        set_default (bool, optional): whether to set the underlying attribute
            default to the default if necessary. The default is ``True`` which
            means to do so.
        prefix (str, optional): the prefix for the underlying attribute

    Returns:
        callable : :any:`classdecorator`
    """

    @classdecorator
    def decorator(decorated_cls):
        attr = "".join((prefix, name))

        def getter(self):
            if set_default:
                try:
                    return getattr(self, attr)
                except AttributeError:
                    setattr(self, attr, default())
                return getattr(self, attr)
            else:
                return getattr(self, attr, default())

        proptype = (lambda x: x) if type is None else type

        def setter(self, new):
            setattr(self, attr, proptype(new))

        def deleter(self):
            try:
                delattr(self, attr)
            except AttributeError:  # pragma: no cover
                pass

        type_doc_str = (
            (":any:`object`" if type is None else type.__name__)
            if type_doc is None
            else type_doc
        )

        getter.__doc__ = "\n\n".join(
            (
                "{doc}",
                ":type: {type_doc}",
                ":getter: {getter}",
                ":setter: {setter}" if type is not None else "",
            )
        ).format(
            doc=("{name} property").format(name=name) if doc is None else doc,
            type_doc=type_doc_str,
            getter=(
                "If no value was set yet, "
                "set it to ``{default}`` and return it."
            ).format(default=repr(default()))
            if set_default
            else (
                "If a value was set yet, return it. "
                " Otherwise return the default value ``{default}``."
            ).format(default=repr(default())),
            setter=("Convert the given value with ``{type_doc}``").format(
                type_doc=type_doc_str
            ),
        )
        prop = property(getter, setter, deleter)
        setattr(decorated_cls, name, prop)
        return decorated_cls

    return decorator


def with_init_from_properties():
    """
    Create a :any:`classdecorator` that **overwrites** the ``__init__``-method
    so that it accepts arguments according to its properties.

    Returns:
        callable : :any:`classdecorator`
    """

    @classdecorator
    def decorator(decorated_cls):
        def __init__(self, **properties):
            cls = type(self)
            for name, prop in get_properties(cls).items():
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

            properties = get_properties(cls)

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
    that it compares all properties for equality.

    Returns:
        callable : :any:`classdecorator`
    """

    @classdecorator
    def decorator(decorated_cls):
        def __eq__(self, other):
            other_properties = get_properties(other)
            for name, prop in get_properties(self).items():
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

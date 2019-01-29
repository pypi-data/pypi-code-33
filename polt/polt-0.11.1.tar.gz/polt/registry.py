# system modules
import collections
import functools
import textwrap
from abc import ABCMeta

# internal modules

# external modules


class RegisteringType(ABCMeta):
    """
    Metaclass adding callables that are marked as ”registered” (i.e. have a
    ``_registered_slot`` attribute) to a ``registry`` class attribute. This
    :attr:`RegisteringType.registry` class attribute is a mapping of classes to
    mappings of slot definitions to functions.

    This metaclass is used for the :any:`FunctionRegistry` class.

    .. note::

        This class inherits from :any:`abc.ABCMeta` so all classes using this
        class as metaclass will behave like :any:`abc.ABC`.

    .. note::

        Implementation based on `this StackOverflow answer
        <https://stackoverflow.com/a/3054505>`_.

    """

    registry = collections.defaultdict(lambda: collections.defaultdict(list))
    """
    Mapping of classes to mappings of slot definitions to functions:

    .. code-block:: python

        registry[class][slot] = [callable1, callable2, ...]

    :type: :class:`collections.defaultdict`
    """

    def __init__(cls, name, bases, attrs):
        for key, val in attrs.items():
            if hasattr(val, "__call__") and hasattr(val, "_registered_slot"):
                cls.registry[cls][val._registered_slot].append(val)


class FunctionRegistry(metaclass=RegisteringType):
    """
    Class with metaclass :any:`RegisteringType` that implements decorators
    to register functions in **class-based** (**not** per instance) slots which
    can be called with :any:`call_registered_functions`.

    .. note::

        Implementation based on `this StackOverflow answer
        <https://stackoverflow.com/a/3054505>`_.

    """

    @classmethod
    def registering_decorator(
        cls, _slot, *args, _on=None, _doc=True, **kwargs
    ):
        """
        Create a registering decorator

        Args:
            _slot (str): the slot to register the function in
            _doc (bool, optional): whether the decorator will prepend a note on
                how the decorated function was registered to its docstring.
                Default is yes.
            _on (str or None, optional): How the decorator will register the
                function:

                ``None``
                    put the decorated function directly into
                    :any:`RegisteringType.registry`
                ``"instance"``
                    register the decorated function so that it will be called
                    with the instance as first argument
                ``"class"``
                    register the decorated function so that it will be called
                    with the class as first argument

            *args: further positional arguments for the function
            **kwargs: further keyword arguments for the function
        """

        def decorator(f):
            assert hasattr(
                f, "__call__"
            ), "This decorator can only be used to decorate callable objects."
            f._registered_slot = _slot
            f._registered_args = args
            f._registered_kwargs = kwargs
            if _doc:
                f.__doc__ = "**Note**: {note_text}\n\n{old_doc}".format(
                    note_text=textwrap.indent(
                        (
                            "This function is registered for the ``{slot}`` "
                            "slot of the :any:`{cls}` class."
                        ).format(
                            slot=_slot,
                            cls=".".join((cls.__module__, cls.__name__)),
                        ),
                        " " * 4,
                    ),
                    old_doc=f.__doc__ or "",
                )
            if _on is None:
                cls.registry[cls][_slot].append(f)
            else:
                f._registered_on = _on
            return f

        return decorator

    @classmethod
    def register_function(cls, _slot, *args, **kwargs):
        """
        Return a decorator registering an arbitrary function to a given slot

        Args:
            _slot (str): the slot to register the function in
            *args: further positional arguments for the function
            **kwargs: further keyword arguments for the function
        """
        return cls.registering_decorator(_slot, *args, **kwargs)

    @classmethod
    def register_method(cls, _slot, *args, **kwargs):
        """
        Return a decorator registering an instance method to a given slot.

        Args:
            _slot (str): the slot to register the method in
            *args: further positional arguments for the function
            **kwargs: further keyword arguments for the function
        """
        return cls.registering_decorator(
            _slot, *args, _on="instance", **kwargs
        )

    @classmethod
    def register_classmethod(cls, _slot, *args, **kwargs):
        """
        Return a decorator registering a classmethod to a given slot.

        Args:
            _slot (str): the slot to register the method in
            *args: further positional arguments for the function
            **kwargs: further keyword arguments for the function
        """
        return cls.registering_decorator(_slot, *args, _on="class", **kwargs)

    def call_registered_functions(self, slot, *args, **kwargs):
        """
        Call all functions of a given slot with their configured arguments.
        Functions registered from classes which this class does not inherit
        from are not executed.

        Args:
            slot (str): the slot to execute the registered functions from
            args, kwargs: further arguments to pass to the functions

        Returns:
            dict : mapping of called functions to their return values
        """
        ret = {}
        for cls, slots in type(self).registry.items():
            if isinstance(self, cls):
                for func in slots.get(slot, tuple()):
                    first_arg = {
                        "instance": (self,),
                        "class": (type(self),),
                    }.get(getattr(func, "_registered_on", None), tuple())
                    reg_args = getattr(func, "_registered_args", tuple())
                    reg_kwargs = getattr(func, "_registered_kwargs", {})
                    func_kwargs = reg_kwargs.copy()
                    func_kwargs.update(kwargs)
                    ret[func] = func(
                        *(first_arg + reg_args + args), **func_kwargs
                    )
        return ret

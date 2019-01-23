#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Implementation of a Remark.
"""
__all__ = ["Remark"]

import collections
import inspect

from metabeyond import hints
from . import _intern
from . import predication


@hints.decorator
class Remark:
    # noinspection PyUnresolvedReferences
    """
    Class that can be subclassed to produce remark decorators that behave similar to Java 6 annotations::

    >>> class Foo(Remark): ...

    >>> @Foo()
    ... def bar():
    ...     pass

    You may also make it accept other parameters.

    >>> class Baz(Remark):
    >>>     def __init__(self, *, x: int, y: int):
    ...         super().__init__()
    ...         self.x = x
    ...         self.y = y

    And decorating with multiple remarks is also supported.

    >>> @Foo()
    ... @Baz(x=122, y=34)  # kwargs work too
    ... def bork():
    ...     pass

    Constraints:

        You can add a single runtime constraint onto a class in order to limit what it is allowed to decorate when used.
        These will be inherited regardless of whether you specify one or not.

        >>> import asyncio
        >>> class SomeRemark(Remark, constraint=asyncio.iscoroutinefunction):
        ...     ...

        >>> @SomeRemark()
        ... async def whatever():
        ...      "This is acceptable!"

        >>> @SomeRemark()
        ... def something_else():
        ...     "This will cause a type error..."

        Or supply multiple constraints in a collection type.

        >>> import asyncio
        >>> import inspect
        >>> class SomeOtherRemark(Remark,
        ...                       constraints=[
        ...                           asyncio.iscoroutinefunction,
        ...                           lambda o: bool(inspect.getdoc(o).strip())
        ...                       ]):
        ...    ...

        Constraints should be callable type `Callable[[ToDecorate], bool]`, meaning they take the decorated
        item as a sole parameter and return True if it is acceptable or False otherwise. They may alternatively
        raise their own exceptions for a more custom interface. Multiple constraints will all have to be True to enable
        the entire check suite to pass.

    Predicates:

        Since v0.1.0, predicates have also been supported in remarks. Predicates are similar to constraints in that they
        are executed across the decorated item when you decorate an object with the remark.

        The distinguishing feature is that whereas constraints will create an error when they fail, a predicate will
        only result in the object not being decorated by the remark if it fails.

        This is useful if you wish to only decorate an object based on some runtime condition, environment variable, or
        flag.

        As the name suggests, a predicate that returns True is considered to be successful, whereas a predicate that
        returns False will be considered to have failed.

        Since v0.2.0, exceptions raised by predicates have been propagated to the caller rather than being interpreted
        as False results.

        Like constraints, a single predicate is provided with the `predicate` kwarg, or multiple predicates can be
        provided with the `predicates` kwarg.

        For example, adding a single predicate:

        >>> import os
        >>> class SomeRemark(Remark, predicate=lambda _: os.getenv('ADD_REMARKS', False)):
        ...    ...

        ... or multiple predicates with the following syntax:

        >>> import os
        >>> class SomeRemark(Remark, predicates=[lambda _: os.getenv('ADD_REMARKS', False), something_else]):
        ...    ...

        This remark would only apply to an object if the `ADD_REMARKS` environment variable was applied at the time
        the object was decorated.

    Warning:
        Passing the `predicate` and `predicates` arguments together in the class definition will cause an error,
        as will `constraint` and `constraints`. This is purely because because I deemed it a stupid thing to be doing.
        You have no need to use both. Make your code reasonable, sensible and readable!

    As of v0.2.0, constraints and predicates may alternatively be specified by defining methods within the class
    with the :attr:`RemarkConstraint` and :attr:`RemarkPredicate` remarks attached to them. This allows defining
    constraints and predicates with the following syntax:

        >>> # Notice how the kwarg constraint will still work
        >>> class SomeRemark(Remark, constraint=inspect.isclass):
        ...     @RemarkConstraint
        ...     def ensure_is_derived_from_foo(self, item_to_annotate):
        ...         return isinstance(item_to_annotate, Foo)
        ...
        ...     @RemarkPredicate
        ...     def only_add_remark_if_var_is_set(self, item_to_annotate):
        ...         return os.getenv('ADD_REMARKS', False)

    The two arguments passed to these methods are `self`, which is the Remark object being called from, and the
    `item_to_annotate` which is the object being decorated by the remark that the predication function is checking.
    """

    def __init__(self) -> None:
        if type(self) is Remark:
            raise TypeError("Please subclass this class first")

    def __init_subclass__(cls, **kwargs) -> None:
        cls._init_constraints(**kwargs)
        cls._init_predicates(**kwargs)

    @classmethod
    def _init_constraints(cls, **kwargs):

        if not hasattr(cls, _intern.CONSTRAINT_ATTR):
            _intern.logger.debug("Applying new constraint mapping to %s", cls)
            constraints = collections.defaultdict(list)
            setattr(cls, _intern.CONSTRAINT_ATTR, constraints)
        else:
            constraints = getattr(cls, _intern.CONSTRAINT_ATTR)

        if _intern.CONSTRAINT_ARG in kwargs and _intern.CONSTRAINTS_ARG in kwargs:
            raise TypeError(
                f"Please specify either {_intern.CONSTRAINTS_ARG} or {_intern.CONSTRAINT_ARG}"
            )
        if _intern.CONSTRAINTS_ARG in kwargs:
            _intern.logger.debug(
                "Adding %s constraints to %s", len(kwargs[_intern.CONSTRAINTS_ARG]), cls
            )
            constraints[cls].extend(kwargs[_intern.CONSTRAINTS_ARG])
        elif _intern.CONSTRAINT_ARG in kwargs:
            _intern.logger.debug("Adding one constraint to %s", cls)
            constraints[cls].append(kwargs[_intern.CONSTRAINT_ARG])

        methods = _intern.members_in_this_class(
            cls, lambda item: isinstance(item, predication.RemarkConstraint)
        )
        constraints[cls].extend(methods)

    @classmethod
    def _init_predicates(cls, **kwargs):
        if not hasattr(cls, _intern.PREDICATE_ATTR):
            _intern.logger.debug("Applying new predicate mapping to %s", cls)
            predicates = collections.defaultdict(list)
            setattr(cls, _intern.PREDICATE_ATTR, predicates)
        else:
            predicates = getattr(cls, _intern.PREDICATE_ATTR)

        if _intern.PREDICATE_ARG in kwargs and _intern.PREDICATES_ARG in kwargs:
            raise TypeError(
                f"Please specify either {_intern.PREDICATES_ARG} or {_intern.PREDICATE_ARG}"
            )
        if _intern.PREDICATES_ARG in kwargs:
            _intern.logger.debug(
                "Adding %s predicates to %s", len(kwargs[_intern.PREDICATES_ARG]), cls
            )
            predicates[cls].extend(kwargs[_intern.PREDICATES_ARG])
        elif _intern.PREDICATE_ARG in kwargs:
            _intern.logger.debug("Adding one predicate to %s", cls)
            predicates[cls].append(kwargs[_intern.PREDICATE_ARG])

        methods = _intern.members_in_this_class(
            cls, lambda item: isinstance(item, predication.RemarkPredicate)
        )
        predicates[cls].extend(methods)

    def __call__(self, item_to_wrap: _intern.ToDecorate) -> _intern.ToDecorate:
        # Apply constraints first.
        self._perform_constraint_checking(item_to_wrap)

        if self._perform_predicate_checking(item_to_wrap):
            if not hasattr(item_to_wrap, _intern.REMARK_COLLECTION_ATTR):
                setattr(item_to_wrap, _intern.REMARK_COLLECTION_ATTR, set())
            getattr(item_to_wrap, _intern.REMARK_COLLECTION_ATTR).add(self)

        return item_to_wrap

    def __repr__(self):
        middle_bit = " ".join(
            f"{k!s}={v!r}" for k, v in self.__dict__.items() if not k.startswith("_")
        )
        return f"{type(self).__name__}({middle_bit})"

    def __hash__(self):
        """
        We hash the class object, this means each class may only be annotated once per remark type.

        This does not take into account transitive inheritance.

        Warning:
             Do not overload this method, otherwise it may cause this framework to misbehave.
        """
        return hash(type(self))

    def __eq__(self, other):
        """
        Compares the class.

        This may seem counter intuitive, but we hash on the class ID anyway. The reason for this is to allow
        a single remark of each type to be allowed on an object only. We must apply an ``__eq__`` overload as
        per https://docs.python.org/3.7/glossary.html#term-hashable

        There is not really a use case for comparing by content value, remark instances usually would be compared
        by their identity with the ``is`` operator instead.

        Warning:
             Do not overload this method, otherwise it may cause this framework to misbehave.
        """
        return hash(self) == hash(other)

    def _perform_constraint_checking(self, item_to_wrap) -> None:
        """
        Checks any constraints on the object and fails if any are not met.
        """
        for enforcing_class, check_list in getattr(self, _intern.CONSTRAINT_ATTR).items():
            for check in check_list:
                if isinstance(check, predication.RemarkConstraint):
                    # Unwrap correctly, as we assume it is an instance method.
                    result = check(self, item_to_wrap)
                else:
                    result = check(item_to_wrap)

                if not result:
                    friendly_item = getattr(item_to_wrap, "__name__", item_to_wrap)
                    friendly_check = getattr(check, "__name__", check)
                    # This error should explain exactly what failed to work...
                    raise TypeError(
                        f'"{type(self).__name__}" cannot be used to decorate "{friendly_item}" because '
                        f'check "{friendly_check}" failed on it, and is required to pass by '
                        f'remark "{enforcing_class.__name__}"'
                    )

    def _perform_predicate_checking(self, item_to_wrap):
        """
        Checks any predicates on this object against the wrapped item. If any
        fail, we return False, else, we return True.
        """
        for enforcing_class, predicate_list in getattr(self, _intern.PREDICATE_ATTR).items():
            for predicate in predicate_list:
                if isinstance(predicate, predication.RemarkPredicate):
                    # Unwrap correctly, as we assume it is an instance method.
                    result = predicate(self, item_to_wrap)
                else:
                    result = predicate(item_to_wrap)

                if not result:
                    _intern.logger.debug(
                        "Predicate %s enforced by %s failed, the object %s will not be marked with "
                        "this remark",
                        predicate,
                        enforcing_class,
                        item_to_wrap,
                    )

                    return False

        else:
            return True

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Mocking utility for quickly stubbing an ABC that is being tested. This is useful for testing mixin classes that
are ABCs where you don't wish to automatically implement each one with a stub method, because that is a lot of
boilerplate code.
"""
import inspect
import textwrap

import asynctest


def _stub_method(method):
    name = method.__name__
    modifier = 'async def' if inspect.iscoroutinefunction(method) else 'def'
    signature = inspect.signature(method)
    params = signature.parameters

    safe_signature = '(' + ', '.join(params.keys()) + ')'

    mock_class = asynctest.MagicMock

    return (
        f'{modifier} {name}{safe_signature}:\n'
        '    """Overrides abstract method"""\n'
        f'    return {mock_class.__module__}.{mock_class.__name__}()\n'
    )


def _stub_property(name, property):
    modifier = 'async def' if inspect.iscoroutinefunction(property.getter) else 'def'
    safe_signature = '(self)'

    mock_class = asynctest.MagicMock

    return (
        '@property\n'
        f'{modifier} {name}{safe_signature}:\n'
        '    """Overrides abstract property getter"""\n'
        f'    return {mock_class.__module__}.{mock_class.__name__}()\n'
    )


def make_abc_mock_class(class_):
    """

    Args:
        class_: the class to stub ABC methods for.
        *args: arguments for the constructor of said class.
        **kwargs: keyword arguments for the constructor of said class.

    Returns:
        A stubbed class for quick mocking. Each method is a stub that returns some mock object immediately.

    Note:
        Asynchronous mocks are implemented using :mod:`asynctest`' coroutine mocks.
    """
    method_stubs = []

    for name, member in inspect.getmembers(class_):
        if not getattr(member, '__isabstractmethod__', False):
            continue
        if inspect.isdatadescriptor(member):
            stub = _stub_property(name, member)
        else:
            stub = _stub_method(member)

        method_stubs.append(stub)

    mock_name = f'{class_.__name__}Mock'

    mock_class_body = f'class {mock_name}(class_):\n' + '\n'.join(
        textwrap.indent(method, '    ') for method in method_stubs
    )

    exec(mock_class_body)  # nosec

    return locals()[mock_name]


def make_abc_mock_instance(class_, *args, **kwargs):
    """
    Args:
        class_: the class to stub ABC methods for.
        *args: arguments for the constructor of said class.
        **kwargs: keyword arguments for the constructor of said class.

    Returns:
        An instance of a stubbed class implementing mocks for each abstract method of the given class for quick mocking.

    Note:
        This will not currently correctly stub properties. Asynchronous mocks are implemented using :mod:`asynctest`'s
        coroutine mocks.
    """
    return make_abc_mock_class(class_)(*args, **kwargs)
